import math
from typing import get_type_hints

import pandas as pd
import pytest

import thalmetis_edr
from thalmetis_edr.bubble_radius import (
    _validate_table3_bubble_radius_grid,
    interpolate_table3_bubble_radius,
)
from thalmetis_edr.results import Table3BubbleRadiusEstimate
from thalmetis_edr.tables import mcrae_2024_table3_inputs


def test_interpolate_table3_bubble_radius_annotation_returns_structured_result() -> (
    None
):
    assert (
        get_type_hints(interpolate_table3_bubble_radius)["return"]
        is Table3BubbleRadiusEstimate
    )


def test_interpolate_table3_bubble_radius_public_api_names_are_exported() -> None:
    exported = set(thalmetis_edr.__all__)

    assert "interpolate_table3_bubble_radius" in exported
    assert "Table3BubbleRadiusInterpolationMetadata" in exported
    assert "Table3BubbleRadiusEstimate" in exported
    assert hasattr(thalmetis_edr, "interpolate_table3_bubble_radius")
    assert hasattr(thalmetis_edr, "Table3BubbleRadiusInterpolationMetadata")
    assert hasattr(thalmetis_edr, "Table3BubbleRadiusEstimate")


def test_interpolate_table3_bubble_radius_exact_grid_point_returns_packaged_value() -> (
    None
):
    inferred_radii = mcrae_2024_table3_inputs()["inferred_radii"]
    packaged_value = float(
        inferred_radii.loc[
            inferred_radii["thread_radius_um"] == 100,
            "inferred_bubble_radius_for_calculator_mm",
        ].iloc[0]
    )

    result = interpolate_table3_bubble_radius(100.0)

    assert result.bubble_radius_mm == pytest.approx(packaged_value)
    assert result.bubble_radius_m == pytest.approx(packaged_value * 1.0e-3)
    assert result.thread_radius_um == pytest.approx(100.0)
    assert result.metadata.exact_grid_point is True
    assert result.metadata.bracketing_thread_radius_um == (100.0, 100.0)


def test_interpolate_table3_bubble_radius_interior_point_matches_manual_loglog_linear_value() -> (  # noqa: E501
    None
):
    result = interpolate_table3_bubble_radius(75.0)

    x1, x2 = math.log10(50.0), math.log10(80.0)
    x = math.log10(75.0)
    z1 = math.log10(0.564231)
    z2 = math.log10(0.834377)
    thread_weight = (x - x1) / (x2 - x1)
    expected = math.pow(10.0, (1.0 - thread_weight) * z1 + thread_weight * z2)

    assert expected == pytest.approx(0.7907364826670179)
    assert result.bubble_radius_mm == pytest.approx(expected)
    assert result.bubble_radius_m == pytest.approx(expected * 1.0e-3)
    assert result.metadata.method == "loglog_linear"
    assert result.metadata.bracketing_thread_radius_um == (50.0, 80.0)


def test_interpolate_table3_bubble_radius_rejects_thread_radius_below_domain() -> None:
    with pytest.raises(ValueError, match="thread_radius_um"):
        interpolate_table3_bubble_radius(9.9)


def test_interpolate_table3_bubble_radius_rejects_thread_radius_above_domain() -> None:
    with pytest.raises(ValueError, match="thread_radius_um"):
        interpolate_table3_bubble_radius(1250.1)


@pytest.mark.parametrize("thread_radius_um", [0.0, -1.0])
def test_interpolate_table3_bubble_radius_rejects_non_positive_input(
    thread_radius_um: float,
) -> None:
    with pytest.raises(ValueError, match="positive"):
        interpolate_table3_bubble_radius(thread_radius_um)


@pytest.mark.parametrize("thread_radius_um", [math.inf, -math.inf, math.nan])
def test_interpolate_table3_bubble_radius_rejects_non_finite_input(
    thread_radius_um: float,
) -> None:
    with pytest.raises(ValueError, match="finite"):
        interpolate_table3_bubble_radius(thread_radius_um)


def test_interpolate_table3_bubble_radius_rejects_unsupported_method() -> None:
    with pytest.raises(ValueError, match="loglog_linear"):
        interpolate_table3_bubble_radius(100.0, method="linear")


def test_interpolate_table3_bubble_radius_metadata_includes_source_table() -> None:
    result = interpolate_table3_bubble_radius(100.0)

    assert "McRae et al. 2024 Table 3" in result.metadata.source_table
    assert "inferred calculator R_b values" in result.metadata.source_table


def test_interpolate_table3_bubble_radius_metadata_includes_source_column() -> None:
    result = interpolate_table3_bubble_radius(100.0)

    assert result.metadata.source_column == "inferred_bubble_radius_for_calculator_mm"


def test_interpolate_table3_bubble_radius_metadata_includes_bracketing_thread_radii() -> (  # noqa: E501
    None
):
    result = interpolate_table3_bubble_radius(75.0)

    assert result.metadata.input_thread_radius_um == pytest.approx(75.0)
    assert result.metadata.bracketing_thread_radius_um == (50.0, 80.0)


def test_interpolate_table3_bubble_radius_metadata_marks_no_extrapolation() -> None:
    result = interpolate_table3_bubble_radius(75.0)

    assert result.metadata.extrapolated is False
    assert result.metadata.domain_min_thread_radius_um == pytest.approx(10.0)
    assert result.metadata.domain_max_thread_radius_um == pytest.approx(1250.0)


def test_interpolate_table3_bubble_radius_warnings_include_stable_scope_terms() -> None:
    result = interpolate_table3_bubble_radius(75.0)
    warning_text = " ".join(result.warnings)

    assert "inferred" in warning_text
    assert "not measured" in warning_text
    assert "Table 3" in warning_text
    assert "No extrapolation" in warning_text
    assert "not a viability prediction" in warning_text


def test_table3_bubble_radius_grid_validation_rejects_missing_required_columns() -> (
    None
):
    inferred_radii = mcrae_2024_table3_inputs()["inferred_radii"].drop(
        columns=["inferred_bubble_radius_for_calculator_mm"]
    )

    with pytest.raises(ValueError, match="missing required columns"):
        _validate_table3_bubble_radius_grid(inferred_radii)


def test_table3_bubble_radius_grid_validation_rejects_duplicate_thread_radii() -> None:
    inferred_radii = mcrae_2024_table3_inputs()["inferred_radii"]
    duplicate = inferred_radii.iloc[[0]]
    inferred_radii = pd.concat([inferred_radii, duplicate], ignore_index=True)

    with pytest.raises(ValueError, match="unique"):
        _validate_table3_bubble_radius_grid(inferred_radii)


def test_table3_bubble_radius_grid_validation_rejects_non_positive_inferred_radii() -> (
    None
):
    inferred_radii = mcrae_2024_table3_inputs()["inferred_radii"]
    inferred_radii.loc[0, "inferred_bubble_radius_for_calculator_mm"] = 0.0

    with pytest.raises(ValueError, match="positive"):
        _validate_table3_bubble_radius_grid(inferred_radii)
