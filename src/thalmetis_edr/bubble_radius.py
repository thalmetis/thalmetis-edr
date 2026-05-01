"""Interpolators for packaged inferred Table 3 calculator bubble radii."""

from __future__ import annotations

import math

import pandas as pd

from thalmetis_edr.published.mcrae_2024 import (
    MCRAE_2024_TABLE3_INFERRED_RADII_SOURCE,
    MCRAE_2024_TABLE_3,
)
from thalmetis_edr.results import (
    Table3BubbleRadiusEstimate,
    Table3BubbleRadiusInterpolationMetadata,
)
from thalmetis_edr.units import mm_to_m

_LOGLOG_LINEAR = "loglog_linear"
_THREAD_RADIUS_COLUMN = "thread_radius_um"
_PUBLISHED_BUBBLE_RADIUS_COLUMN = "published_bubble_radius_mm"
_INFERRED_BUBBLE_RADIUS_COLUMN = "inferred_bubble_radius_for_calculator_mm"
_REQUIRED_COLUMNS = (
    _THREAD_RADIUS_COLUMN,
    _PUBLISHED_BUBBLE_RADIUS_COLUMN,
    _INFERRED_BUBBLE_RADIUS_COLUMN,
)
_GRID_EQUALITY_REL_TOL = 1.0e-12
_GRID_EQUALITY_ABS_TOL = 0.0

_INTERPOLATION_ASSUMPTIONS = (
    (
        "Uses packaged inferred Table 3 calculator R_b values from the v0.1 "
        "Table 3 reconciliation, not measured or raw bubble-radius data."
    ),
    (
        "Interpolates the inferred calculator R_b fixture only; this is not a "
        "general sparger bubble-size predictor."
    ),
    (
        "In later viability workflows, user-supplied bubble radius should be "
        "preferred when available."
    ),
)
_INTERPOLATION_WARNINGS = (
    (
        "Table 3 bubble-radius interpolation uses inferred calculator R_b "
        "values from the v0.1 reconciliation, not measured bubble-radius data."
    ),
    "No extrapolation is performed outside the packaged Table 3 radius domain.",
    (
        "This primitive is not a viability prediction and is not a general "
        "sparger bubble-size predictor."
    ),
)


def _grid_value_isclose(left: float, right: float) -> bool:
    return math.isclose(
        left,
        right,
        rel_tol=_GRID_EQUALITY_REL_TOL,
        abs_tol=_GRID_EQUALITY_ABS_TOL,
    )


def _ensure_finite_positive(value: float, name: str) -> float:
    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be finite and positive.") from exc
    if not math.isfinite(numeric_value) or numeric_value <= 0.0:
        raise ValueError(f"{name} must be finite and positive.")
    return numeric_value


def _validate_table3_bubble_radius_grid(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a sorted numeric inferred Table 3 bubble-radius grid."""
    missing_columns = [column for column in _REQUIRED_COLUMNS if column not in frame]
    if missing_columns:
        raise ValueError(
            "Table 3 bubble-radius grid is missing required columns: "
            f"{missing_columns}."
        )

    grid = frame.loc[:, list(_REQUIRED_COLUMNS)].copy(deep=True)
    for column in _REQUIRED_COLUMNS:
        grid[column] = pd.to_numeric(grid[column], errors="raise")
        if grid[column].isna().any():
            raise ValueError(
                f"Table 3 bubble-radius column {column!r} has missing data."
            )
        if not grid[column].map(math.isfinite).all():
            raise ValueError(
                f"Table 3 bubble-radius column {column!r} has non-finite values."
            )
        if (grid[column] <= 0.0).any():
            raise ValueError(
                f"Table 3 bubble-radius column {column!r} must be positive."
            )

    if grid[_THREAD_RADIUS_COLUMN].duplicated().any():
        raise ValueError("Table 3 bubble-radius thread radii must be unique.")

    return grid.sort_values(_THREAD_RADIUS_COLUMN).reset_index(drop=True)


def _bracket_thread_radius(
    thread_radius_um: float, thread_grid: tuple[float, ...]
) -> tuple[float, float]:
    for grid_value in thread_grid:
        if _grid_value_isclose(thread_radius_um, grid_value):
            return (grid_value, grid_value)

    domain_min = thread_grid[0]
    domain_max = thread_grid[-1]
    if thread_radius_um < domain_min or thread_radius_um > domain_max:
        raise ValueError(
            "thread_radius_um must be within the packaged Table 3 bubble-radius "
            f"domain [{domain_min}, {domain_max}]."
        )

    for lower, upper in zip(thread_grid, thread_grid[1:], strict=False):
        if lower < thread_radius_um < upper:
            return (lower, upper)

    raise ValueError(
        "Could not bracket thread_radius_um in the packaged Table 3 bubble-radius grid."
    )


def _bubble_radius_at_grid_point(
    grid: pd.DataFrame, *, thread_radius_um: float
) -> float:
    rows = grid[
        grid[_THREAD_RADIUS_COLUMN].map(
            lambda value: _grid_value_isclose(float(value), thread_radius_um)
        )
    ]
    if len(rows) != 1:
        raise ValueError(
            "No unique packaged Table 3 bubble-radius row for thread radius "
            f"{thread_radius_um}."
        )
    bubble_radius_mm = float(rows.iloc[0][_INFERRED_BUBBLE_RADIUS_COLUMN])
    _ensure_finite_positive(bubble_radius_mm, "inferred bubble radius")
    return bubble_radius_mm


def interpolate_table3_bubble_radius(
    thread_radius_um: float,
    method: str = _LOGLOG_LINEAR,
) -> Table3BubbleRadiusEstimate:
    """Interpolate packaged inferred Table 3 calculator R_b values."""
    if method != _LOGLOG_LINEAR:
        raise ValueError("Only method='loglog_linear' is supported.")

    input_thread_radius_um = _ensure_finite_positive(
        thread_radius_um, "thread_radius_um"
    )

    from thalmetis_edr.tables import mcrae_2024_table3_inputs

    grid = _validate_table3_bubble_radius_grid(
        mcrae_2024_table3_inputs()["inferred_radii"]
    )
    thread_grid = tuple(float(value) for value in grid[_THREAD_RADIUS_COLUMN].tolist())
    domain_min_thread = thread_grid[0]
    domain_max_thread = thread_grid[-1]

    if (
        input_thread_radius_um < domain_min_thread
        or input_thread_radius_um > domain_max_thread
    ):
        raise ValueError(
            "thread_radius_um must be within the packaged Table 3 bubble-radius "
            f"domain [{domain_min_thread}, {domain_max_thread}]."
        )

    thread_bracket = _bracket_thread_radius(input_thread_radius_um, thread_grid)
    exact_grid_point = _grid_value_isclose(thread_bracket[0], thread_bracket[1])

    if exact_grid_point:
        bubble_radius_mm = _bubble_radius_at_grid_point(
            grid, thread_radius_um=thread_bracket[0]
        )
    else:
        lower, upper = thread_bracket
        lower_radius_mm = _bubble_radius_at_grid_point(grid, thread_radius_um=lower)
        upper_radius_mm = _bubble_radius_at_grid_point(grid, thread_radius_um=upper)
        weight = (math.log10(input_thread_radius_um) - math.log10(lower)) / (
            math.log10(upper) - math.log10(lower)
        )
        log_bubble_radius_mm = (1.0 - weight) * math.log10(
            lower_radius_mm
        ) + weight * math.log10(upper_radius_mm)
        bubble_radius_mm = math.pow(10.0, log_bubble_radius_mm)

    metadata = Table3BubbleRadiusInterpolationMetadata(
        method=method,
        source_table=f"{MCRAE_2024_TABLE_3}: {MCRAE_2024_TABLE3_INFERRED_RADII_SOURCE}",
        source_column=_INFERRED_BUBBLE_RADIUS_COLUMN,
        input_thread_radius_um=input_thread_radius_um,
        bracketing_thread_radius_um=thread_bracket,
        exact_grid_point=exact_grid_point,
        interpolation_space="log10(thread_radius_um), log10(bubble_radius_mm)",
        domain_min_thread_radius_um=domain_min_thread,
        domain_max_thread_radius_um=domain_max_thread,
        extrapolated=False,
        warnings=_INTERPOLATION_WARNINGS,
    )
    return Table3BubbleRadiusEstimate(
        bubble_radius_mm=bubble_radius_mm,
        bubble_radius_m=mm_to_m(bubble_radius_mm),
        thread_radius_um=input_thread_radius_um,
        metadata=metadata,
        assumptions=_INTERPOLATION_ASSUMPTIONS,
        warnings=_INTERPOLATION_WARNINGS,
    )
