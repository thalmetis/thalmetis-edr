"""Affected-volume helpers for bounded published sources."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from thalmetis_edr.published.mcrae_2024 import (
    MCRAE_2024_EQ_2,
    MCRAE_2024_FIGURE5A_SOURCE,
    MCRAE_2024_FIGURE_5A,
)
from thalmetis_edr.published.walls_2017 import WALLS_2017_AFFECTED_VOLUME_CONTEXT
from thalmetis_edr.results import (
    AffectedVolumeResult,
    InterpolationMetadata,
    PinchoffAffectedVolumeEstimate,
)
from thalmetis_edr.units import nl_to_m3

_LOGLOG_BILINEAR = "loglog_bilinear"
_THREAD_RADIUS_COLUMN = "thread_radius_um"
_THRESHOLD_TO_COLUMN: dict[float, str] = {
    1.0e6: "affected_volume_1e6_nl",
    1.0e7: "affected_volume_1e7_nl",
    1.0e8: "affected_volume_1e8_nl",
}
_REQUIRED_FIGURE5A_COLUMNS = (
    _THREAD_RADIUS_COLUMN,
    *_THRESHOLD_TO_COLUMN.values(),
)
_GRID_EQUALITY_REL_TOL = 1.0e-12
_GRID_EQUALITY_ABS_TOL = 0.0

_INTERPOLATION_ASSUMPTIONS = (
    (
        "Uses packaged McRae 2024 Figure 5a pathway data inferred during the "
        "v0.1 reconciliation from a near-final author script, not raw original "
        "simulation output."
    ),
    "Interpolates affected volume only; no viability estimate is calculated.",
    "Log-space interpolation is used for sensitivity analysis within the grid.",
)
_INTERPOLATION_WARNINGS = (
    (
        "Figure 5a affected-volume interpolation is a sensitivity-analysis "
        "primitive, not a validated industrial viability predictor."
    ),
    "No extrapolation is performed outside the packaged Figure 5a domain.",
)


def _grid_value_isclose(left: float, right: float) -> bool:
    return math.isclose(
        left,
        right,
        rel_tol=_GRID_EQUALITY_REL_TOL,
        abs_tol=_GRID_EQUALITY_ABS_TOL,
    )


def _ensure_finite_positive(value: float, name: str) -> float:
    numeric_value = float(value)
    if not math.isfinite(numeric_value) or numeric_value <= 0.0:
        raise ValueError(f"{name} must be finite and positive.")
    return numeric_value


def _validate_figure5a_grid(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a sorted numeric Figure 5a grid or raise ValueError."""
    missing_columns = [
        column for column in _REQUIRED_FIGURE5A_COLUMNS if column not in frame.columns
    ]
    if missing_columns:
        raise ValueError(
            "Figure 5a affected-volume grid is missing required columns: "
            f"{missing_columns}."
        )

    thresholds = tuple(float(threshold) for threshold in _THRESHOLD_TO_COLUMN)
    if thresholds != tuple(sorted(thresholds)) or len(set(thresholds)) != len(
        thresholds
    ):
        raise ValueError(
            "Figure 5a threshold grid must be numeric, unique, and sorted."
        )
    for threshold in thresholds:
        _ensure_finite_positive(threshold, "Figure 5a EDR threshold")

    grid = frame.loc[:, list(_REQUIRED_FIGURE5A_COLUMNS)].copy(deep=True)
    for column in _REQUIRED_FIGURE5A_COLUMNS:
        grid[column] = pd.to_numeric(grid[column], errors="raise")
        if grid[column].isna().any():
            raise ValueError(f"Figure 5a grid column {column!r} contains missing data.")
        if not grid[column].map(math.isfinite).all():
            raise ValueError(
                f"Figure 5a grid column {column!r} contains non-finite values."
            )

    if grid[_THREAD_RADIUS_COLUMN].duplicated().any():
        raise ValueError("Figure 5a thread radii must be unique.")
    if (grid[_THREAD_RADIUS_COLUMN] <= 0.0).any():
        raise ValueError("Figure 5a thread radii must be positive.")

    volume_columns = list(_THRESHOLD_TO_COLUMN.values())
    if (grid.loc[:, volume_columns] <= 0.0).any().any():
        raise ValueError("Figure 5a affected-volume values must be positive.")

    return grid.sort_values(_THREAD_RADIUS_COLUMN).reset_index(drop=True)


def _bracket_value(
    value: float, grid_values: tuple[float, ...], name: str
) -> tuple[float, float]:
    for grid_value in grid_values:
        if _grid_value_isclose(value, grid_value):
            return (grid_value, grid_value)

    domain_min = grid_values[0]
    domain_max = grid_values[-1]
    if value < domain_min or value > domain_max:
        raise ValueError(
            f"{name} must be within the packaged Figure 5a domain "
            f"[{domain_min}, {domain_max}]."
        )

    for lower, upper in zip(grid_values, grid_values[1:], strict=False):
        if lower < value < upper:
            return (lower, upper)

    raise ValueError(f"Could not bracket {name} in the packaged Figure 5a grid.")


def _threshold_column(threshold: float) -> str:
    for grid_threshold, column in _THRESHOLD_TO_COLUMN.items():
        if _grid_value_isclose(threshold, grid_threshold):
            return column
    raise ValueError(f"No packaged Figure 5a column for threshold {threshold}.")


def _affected_volume_at_grid_point(
    grid: pd.DataFrame,
    *,
    thread_radius_um: float,
    edr_threshold_w_m3: float,
) -> float:
    thread_rows = grid[
        grid[_THREAD_RADIUS_COLUMN].map(
            lambda value: _grid_value_isclose(float(value), thread_radius_um)
        )
    ]
    if len(thread_rows) != 1:
        raise ValueError(
            f"No unique packaged Figure 5a row for thread radius {thread_radius_um}."
        )
    affected_volume_nl = float(
        thread_rows.iloc[0][_threshold_column(edr_threshold_w_m3)]
    )
    _ensure_finite_positive(affected_volume_nl, "Figure 5a affected volume")
    return affected_volume_nl


def _log_linear_interpolate(
    *,
    value: float,
    lower: float,
    upper: float,
    lower_result: float,
    upper_result: float,
) -> float:
    if _grid_value_isclose(lower, upper):
        return lower_result
    weight = (math.log10(value) - math.log10(lower)) / (
        math.log10(upper) - math.log10(lower)
    )
    log_result = (1.0 - weight) * math.log10(lower_result) + weight * math.log10(
        upper_result
    )
    return math.pow(10.0, log_result)


def interpolate_pinchoff_affected_volume(
    thread_radius_um: float,
    edr_threshold_w_m3: float,
    method: str = _LOGLOG_BILINEAR,
) -> PinchoffAffectedVolumeEstimate:
    """Interpolate packaged McRae 2024 Figure 5a affected volume."""
    if method != _LOGLOG_BILINEAR:
        raise ValueError("Only method='loglog_bilinear' is supported.")

    input_thread_radius_um = _ensure_finite_positive(
        thread_radius_um, "thread_radius_um"
    )
    input_edr_threshold_w_m3 = _ensure_finite_positive(
        edr_threshold_w_m3, "edr_threshold_w_m3"
    )

    from thalmetis_edr.tables import mcrae_2024_figure5a_volumes

    grid = _validate_figure5a_grid(mcrae_2024_figure5a_volumes())
    thread_grid = tuple(float(value) for value in grid[_THREAD_RADIUS_COLUMN].tolist())
    threshold_grid = tuple(float(value) for value in _THRESHOLD_TO_COLUMN)

    domain_min_thread = thread_grid[0]
    domain_max_thread = thread_grid[-1]
    domain_min_threshold = threshold_grid[0]
    domain_max_threshold = threshold_grid[-1]
    if (
        input_thread_radius_um < domain_min_thread
        or input_thread_radius_um > domain_max_thread
    ):
        raise ValueError(
            "thread_radius_um must be within the packaged Figure 5a domain "
            f"[{domain_min_thread}, {domain_max_thread}]."
        )
    if (
        input_edr_threshold_w_m3 < domain_min_threshold
        or input_edr_threshold_w_m3 > domain_max_threshold
    ):
        raise ValueError(
            "edr_threshold_w_m3 must be within the packaged Figure 5a domain "
            f"[{domain_min_threshold}, {domain_max_threshold}]."
        )

    thread_bracket = _bracket_value(
        input_thread_radius_um, thread_grid, "thread_radius_um"
    )
    threshold_bracket = _bracket_value(
        input_edr_threshold_w_m3, threshold_grid, "edr_threshold_w_m3"
    )
    exact_thread = _grid_value_isclose(thread_bracket[0], thread_bracket[1])
    exact_threshold = _grid_value_isclose(threshold_bracket[0], threshold_bracket[1])

    if exact_thread and exact_threshold:
        affected_volume_nl = _affected_volume_at_grid_point(
            grid,
            thread_radius_um=thread_bracket[0],
            edr_threshold_w_m3=threshold_bracket[0],
        )
    elif exact_thread:
        lower_volume = _affected_volume_at_grid_point(
            grid,
            thread_radius_um=thread_bracket[0],
            edr_threshold_w_m3=threshold_bracket[0],
        )
        upper_volume = _affected_volume_at_grid_point(
            grid,
            thread_radius_um=thread_bracket[0],
            edr_threshold_w_m3=threshold_bracket[1],
        )
        affected_volume_nl = _log_linear_interpolate(
            value=input_edr_threshold_w_m3,
            lower=threshold_bracket[0],
            upper=threshold_bracket[1],
            lower_result=lower_volume,
            upper_result=upper_volume,
        )
    elif exact_threshold:
        lower_volume = _affected_volume_at_grid_point(
            grid,
            thread_radius_um=thread_bracket[0],
            edr_threshold_w_m3=threshold_bracket[0],
        )
        upper_volume = _affected_volume_at_grid_point(
            grid,
            thread_radius_um=thread_bracket[1],
            edr_threshold_w_m3=threshold_bracket[0],
        )
        affected_volume_nl = _log_linear_interpolate(
            value=input_thread_radius_um,
            lower=thread_bracket[0],
            upper=thread_bracket[1],
            lower_result=lower_volume,
            upper_result=upper_volume,
        )
    else:
        x_lower, x_upper = thread_bracket
        y_lower, y_upper = threshold_bracket
        z_lower_lower = math.log10(
            _affected_volume_at_grid_point(
                grid,
                thread_radius_um=x_lower,
                edr_threshold_w_m3=y_lower,
            )
        )
        z_upper_lower = math.log10(
            _affected_volume_at_grid_point(
                grid,
                thread_radius_um=x_upper,
                edr_threshold_w_m3=y_lower,
            )
        )
        z_lower_upper = math.log10(
            _affected_volume_at_grid_point(
                grid,
                thread_radius_um=x_lower,
                edr_threshold_w_m3=y_upper,
            )
        )
        z_upper_upper = math.log10(
            _affected_volume_at_grid_point(
                grid,
                thread_radius_um=x_upper,
                edr_threshold_w_m3=y_upper,
            )
        )
        thread_weight = (math.log10(input_thread_radius_um) - math.log10(x_lower)) / (
            math.log10(x_upper) - math.log10(x_lower)
        )
        threshold_weight = (
            math.log10(input_edr_threshold_w_m3) - math.log10(y_lower)
        ) / (math.log10(y_upper) - math.log10(y_lower))
        log_affected_volume = (
            (1.0 - thread_weight) * (1.0 - threshold_weight) * z_lower_lower
            + thread_weight * (1.0 - threshold_weight) * z_upper_lower
            + (1.0 - thread_weight) * threshold_weight * z_lower_upper
            + thread_weight * threshold_weight * z_upper_upper
        )
        affected_volume_nl = math.pow(10.0, log_affected_volume)

    metadata = InterpolationMetadata(
        method=method,
        source_table=f"{MCRAE_2024_FIGURE_5A}: {MCRAE_2024_FIGURE5A_SOURCE}",
        input_thread_radius_um=input_thread_radius_um,
        input_edr_threshold_w_m3=input_edr_threshold_w_m3,
        bracketing_thread_radius_um=thread_bracket,
        bracketing_edr_threshold_w_m3=threshold_bracket,
        exact_grid_point=exact_thread and exact_threshold,
        interpolation_space="log10(thread_radius_um), log10(edr_threshold_w_m3), "
        "log10(affected_volume_nl)",
        domain_min_thread_radius_um=domain_min_thread,
        domain_max_thread_radius_um=domain_max_thread,
        domain_min_edr_threshold_w_m3=domain_min_threshold,
        domain_max_edr_threshold_w_m3=domain_max_threshold,
        extrapolated=False,
        warnings=_INTERPOLATION_WARNINGS,
    )

    return PinchoffAffectedVolumeEstimate(
        affected_volume_nl=affected_volume_nl,
        affected_volume_m3=nl_to_m3(affected_volume_nl),
        thread_radius_um=input_thread_radius_um,
        edr_threshold_w_m3=input_edr_threshold_w_m3,
        metadata=metadata,
        assumptions=_INTERPOLATION_ASSUMPTIONS,
        warnings=_INTERPOLATION_WARNINGS,
    )


def affected_volume_from_threshold(
    *,
    threshold_edr_w_m3: float | None = None,
    source: str = MCRAE_2024_EQ_2,
    **inputs: Any,
) -> AffectedVolumeResult:
    """Scaffold McRae 2024 pinch-off affected-volume calculation.

    The v0.1 package exposes the result shape and source metadata only. The
    published equation is intentionally not implemented in this PR.
    """
    raise NotImplementedError(
        "McRae et al. 2024 affected-volume equations are out of scope for the "
        "bounded v0.1 implementation."
    )


def walls_2017_rupture_affected_volume(
    *,
    threshold_edr_w_m3: float | None = None,
    source: str = WALLS_2017_AFFECTED_VOLUME_CONTEXT,
    **inputs: Any,
) -> AffectedVolumeResult:
    """Affected-volume-only placeholder for possible Walls 2017 support.

    This is not a rupture viability model. Future implementation is allowed
    only if it can be derived directly from published Walls et al. 2017
    equations, data, or figures, and it must return affected-volume-style
    results only.
    """
    raise NotImplementedError(
        "Walls et al. 2017 rupture affected-volume support is scaffold-only "
        "and does not implement rupture viability in v0.1."
    )
