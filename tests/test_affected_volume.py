import math
from typing import get_type_hints

import pandas as pd
import pytest

import thalmetis_edr
from thalmetis_edr.affected_volume import (
    _validate_figure5a_grid,
    affected_volume_from_threshold,
    interpolate_pinchoff_affected_volume,
    walls_2017_rupture_affected_volume,
)
from thalmetis_edr.results import AffectedVolumeResult, PinchoffAffectedVolumeEstimate
from thalmetis_edr.tables import mcrae_2024_figure5a_volumes


def test_affected_volume_stubs_return_structured_annotations() -> None:
    assert (
        get_type_hints(affected_volume_from_threshold)["return"] is AffectedVolumeResult
    )
    assert (
        get_type_hints(walls_2017_rupture_affected_volume)["return"]
        is AffectedVolumeResult
    )


def test_interpolate_pinchoff_affected_volume_annotation_returns_structured_result() -> (  # noqa: E501
    None
):
    assert (
        get_type_hints(interpolate_pinchoff_affected_volume)["return"]
        is PinchoffAffectedVolumeEstimate
    )


def test_interpolate_pinchoff_public_api_names_are_exported() -> None:
    exported = set(thalmetis_edr.__all__)

    assert "interpolate_pinchoff_affected_volume" in exported
    assert "InterpolationMetadata" in exported
    assert "PinchoffAffectedVolumeEstimate" in exported
    assert hasattr(thalmetis_edr, "interpolate_pinchoff_affected_volume")
    assert hasattr(thalmetis_edr, "InterpolationMetadata")
    assert hasattr(thalmetis_edr, "PinchoffAffectedVolumeEstimate")


def test_affected_volume_stubs_are_scaffold_only() -> None:
    with pytest.raises(NotImplementedError):
        affected_volume_from_threshold()

    with pytest.raises(NotImplementedError):
        walls_2017_rupture_affected_volume()


def test_interpolate_pinchoff_exact_grid_point_returns_packaged_value() -> None:
    figure5a = mcrae_2024_figure5a_volumes()
    packaged_value = float(
        figure5a.loc[
            figure5a["thread_radius_um"] == 100,
            "affected_volume_1e7_nl",
        ].iloc[0]
    )

    result = interpolate_pinchoff_affected_volume(100.0, 1.0e7)

    assert result.affected_volume_nl == pytest.approx(packaged_value)
    assert result.affected_volume_m3 == pytest.approx(packaged_value * 1.0e-12)
    assert result.metadata.exact_grid_point is True
    assert result.metadata.bracketing_thread_radius_um == (100.0, 100.0)
    assert result.metadata.bracketing_edr_threshold_w_m3 == (1.0e7, 1.0e7)


def test_interpolate_pinchoff_one_axis_exact_uses_log_linear_interpolation() -> None:
    result = interpolate_pinchoff_affected_volume(75.0, 1.0e7)

    expected = 1.6901548170541272

    assert result.affected_volume_nl == pytest.approx(expected)
    assert result.metadata.method == "loglog_bilinear"
    assert result.metadata.exact_grid_point is False
    assert result.metadata.bracketing_thread_radius_um == (50.0, 80.0)
    assert result.metadata.bracketing_edr_threshold_w_m3 == (1.0e7, 1.0e7)


def test_interpolate_pinchoff_interior_point_matches_manual_loglog_bilinear_value() -> (
    None
):
    result = interpolate_pinchoff_affected_volume(75.0, 5.0e6)

    x1, x2 = math.log10(50.0), math.log10(80.0)
    y1, y2 = math.log10(1.0e6), math.log10(1.0e7)
    x, y = math.log10(75.0), math.log10(5.0e6)
    z11 = math.log10(5.33482558584271)
    z21 = math.log10(11.230812054158598)
    z12 = math.log10(1.1081922590524727)
    z22 = math.log10(1.8076088061464917)
    thread_weight = (x - x1) / (x2 - x1)
    threshold_weight = (y - y1) / (y2 - y1)
    expected = math.pow(
        10.0,
        (1.0 - thread_weight) * (1.0 - threshold_weight) * z11
        + thread_weight * (1.0 - threshold_weight) * z21
        + (1.0 - thread_weight) * threshold_weight * z12
        + thread_weight * threshold_weight * z22,
    )

    assert expected == pytest.approx(2.8983812912876088)
    assert result.affected_volume_nl == pytest.approx(expected)
    assert result.affected_volume_m3 == pytest.approx(expected * 1.0e-12)
    assert result.metadata.exact_grid_point is False


def test_interpolate_pinchoff_rejects_threshold_below_domain() -> None:
    with pytest.raises(ValueError, match="edr_threshold_w_m3"):
        interpolate_pinchoff_affected_volume(100.0, 9.9e5)


def test_interpolate_pinchoff_rejects_threshold_above_domain() -> None:
    with pytest.raises(ValueError, match="edr_threshold_w_m3"):
        interpolate_pinchoff_affected_volume(100.0, 1.1e8)


def test_interpolate_pinchoff_rejects_thread_radius_below_domain() -> None:
    with pytest.raises(ValueError, match="thread_radius_um"):
        interpolate_pinchoff_affected_volume(9.9, 1.0e7)


def test_interpolate_pinchoff_rejects_thread_radius_above_domain() -> None:
    with pytest.raises(ValueError, match="thread_radius_um"):
        interpolate_pinchoff_affected_volume(1250.1, 1.0e7)


@pytest.mark.parametrize(
    ("thread_radius_um", "edr_threshold_w_m3"),
    [
        (0.0, 1.0e7),
        (-1.0, 1.0e7),
        (100.0, 0.0),
        (100.0, -1.0),
    ],
)
def test_interpolate_pinchoff_rejects_non_positive_inputs(
    thread_radius_um: float, edr_threshold_w_m3: float
) -> None:
    with pytest.raises(ValueError, match="positive"):
        interpolate_pinchoff_affected_volume(thread_radius_um, edr_threshold_w_m3)


def test_interpolate_pinchoff_rejects_unsupported_method() -> None:
    with pytest.raises(ValueError, match="loglog_bilinear"):
        interpolate_pinchoff_affected_volume(100.0, 1.0e7, method="linear")


def test_interpolate_pinchoff_metadata_includes_source_table() -> None:
    result = interpolate_pinchoff_affected_volume(100.0, 1.0e7)

    assert "McRae et al. 2024 Figure 5a" in result.metadata.source_table
    assert "near-final author-script" in result.metadata.source_table


def test_interpolate_pinchoff_metadata_includes_bracketing_thread_radii() -> None:
    result = interpolate_pinchoff_affected_volume(75.0, 5.0e6)

    assert result.thread_radius_um == pytest.approx(75.0)
    assert result.metadata.input_thread_radius_um == pytest.approx(75.0)
    assert result.metadata.bracketing_thread_radius_um == (50.0, 80.0)


def test_interpolate_pinchoff_metadata_includes_bracketing_thresholds() -> None:
    result = interpolate_pinchoff_affected_volume(75.0, 5.0e6)

    assert result.edr_threshold_w_m3 == pytest.approx(5.0e6)
    assert result.metadata.input_edr_threshold_w_m3 == pytest.approx(5.0e6)
    assert result.metadata.bracketing_edr_threshold_w_m3 == (1.0e6, 1.0e7)


def test_interpolate_pinchoff_metadata_marks_no_extrapolation() -> None:
    result = interpolate_pinchoff_affected_volume(75.0, 5.0e6)

    assert result.metadata.extrapolated is False
    assert result.metadata.domain_min_thread_radius_um == pytest.approx(10.0)
    assert result.metadata.domain_max_thread_radius_um == pytest.approx(1250.0)
    assert result.metadata.domain_min_edr_threshold_w_m3 == pytest.approx(1.0e6)
    assert result.metadata.domain_max_edr_threshold_w_m3 == pytest.approx(1.0e8)


def test_interpolate_pinchoff_warnings_include_stable_scope_terms() -> None:
    result = interpolate_pinchoff_affected_volume(75.0, 5.0e6)
    warning_text = " ".join(result.warnings)

    assert "sensitivity" in warning_text
    assert "not a validated" in warning_text
    assert "No extrapolation" in warning_text
    assert "Figure 5a" in warning_text


def test_figure5a_grid_validation_rejects_missing_required_columns() -> None:
    figure5a = mcrae_2024_figure5a_volumes().drop(columns=["affected_volume_1e7_nl"])

    with pytest.raises(ValueError, match="missing required columns"):
        _validate_figure5a_grid(figure5a)


def test_figure5a_grid_validation_rejects_duplicate_thread_radii() -> None:
    figure5a = mcrae_2024_figure5a_volumes()
    duplicate = figure5a.iloc[[0]]
    figure5a = pd.concat([figure5a, duplicate], ignore_index=True)

    with pytest.raises(ValueError, match="unique"):
        _validate_figure5a_grid(figure5a)


def test_figure5a_grid_validation_rejects_non_positive_affected_volumes() -> None:
    figure5a = mcrae_2024_figure5a_volumes()
    figure5a.loc[0, "affected_volume_1e7_nl"] = 0.0

    with pytest.raises(ValueError, match="positive"):
        _validate_figure5a_grid(figure5a)
