import math
from typing import get_type_hints

import pytest

import thalmetis_edr
from thalmetis_edr.bubble_radius import interpolate_table3_bubble_radius
from thalmetis_edr.pinchoff import estimate_pinchoff_viability
from thalmetis_edr.results import PinchoffViabilityEstimate
from thalmetis_edr.units import liters_to_m3, mm_to_m


def _estimate(**overrides: object) -> PinchoffViabilityEstimate:
    inputs = {
        "thread_radius_um": 100.0,
        "edr_threshold_w_m3": 1.0e7,
        "system_volume_l": 100.0,
        "initial_viability_pct": 95.0,
        "single_event_viability_loss_pct": 10.0,
        "total_gas_volume_l": 1.0,
        "bubble_radius_mm": 1.0,
    }
    inputs.update(overrides)
    return estimate_pinchoff_viability(**inputs)


def test_estimate_pinchoff_viability_public_api_names_are_exported() -> None:
    exported = set(thalmetis_edr.__all__)

    assert "estimate_pinchoff_viability" in exported
    assert "PinchoffViabilityEstimate" in exported
    assert hasattr(thalmetis_edr, "estimate_pinchoff_viability")
    assert hasattr(thalmetis_edr, "PinchoffViabilityEstimate")


def test_estimate_pinchoff_viability_annotation_returns_structured_result() -> None:
    assert (
        get_type_hints(estimate_pinchoff_viability)["return"]
        is PinchoffViabilityEstimate
    )


def test_estimate_pinchoff_viability_returns_structured_result_object() -> None:
    result = _estimate()

    assert isinstance(result, PinchoffViabilityEstimate)
    assert result.thread_radius_um == pytest.approx(100.0)
    assert result.edr_threshold_w_m3 == pytest.approx(1.0e7)


def test_user_supplied_bubble_radius_is_preferred() -> None:
    result = _estimate(bubble_radius_mm=0.5)

    assert result.bubble_radius_mm == pytest.approx(0.5)
    assert result.bubble_radius_source == "user_supplied"
    assert result.bubble_radius_metadata is None
    assert "not enforced" in " ".join(result.assumptions)


def test_user_supplied_bubble_radius_does_not_call_inferred_radius_interpolator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_called(thread_radius_um: float) -> object:
        raise AssertionError(f"unexpected inferred radius call: {thread_radius_um}")

    monkeypatch.setattr(
        "thalmetis_edr.pinchoff.interpolate_table3_bubble_radius",
        fail_if_called,
    )

    result = _estimate(bubble_radius_mm=0.5)

    assert result.bubble_radius_source == "user_supplied"


def test_inferred_table3_bubble_radius_is_used_only_when_user_radius_is_absent() -> (
    None
):
    result = _estimate(bubble_radius_mm=None)
    expected = interpolate_table3_bubble_radius(100.0)

    assert result.bubble_radius_source == "inferred_table3_interpolation"
    assert result.bubble_radius_mm == pytest.approx(expected.bubble_radius_mm)
    assert result.bubble_radius_metadata is not None


def test_missing_bubble_radius_raises_when_fallback_is_disabled() -> None:
    with pytest.raises(ValueError, match="bubble_radius_mm"):
        _estimate(bubble_radius_mm=None, use_inferred_bubble_radius=False)


def test_affected_volume_metadata_is_preserved() -> None:
    result = _estimate(thread_radius_um=75.0, edr_threshold_w_m3=5.0e6)

    assert result.affected_volume_metadata.input_thread_radius_um == pytest.approx(75.0)
    assert result.affected_volume_metadata.input_edr_threshold_w_m3 == pytest.approx(
        5.0e6
    )
    assert result.affected_volume_metadata.method == "loglog_bilinear"


def test_inferred_bubble_radius_metadata_is_preserved_when_used() -> None:
    result = _estimate(bubble_radius_mm=None, thread_radius_um=75.0)

    assert result.bubble_radius_metadata is not None
    assert result.bubble_radius_metadata.input_thread_radius_um == pytest.approx(75.0)
    assert result.bubble_radius_metadata.method == "loglog_linear"


def test_bubble_radius_metadata_is_none_for_user_supplied_radius() -> None:
    result = _estimate(bubble_radius_mm=0.5)

    assert result.bubble_radius_metadata is None


def test_direct_total_gas_volume_mode() -> None:
    result = _estimate(total_gas_volume_l=12.5)

    assert result.gas_exposure_mode == "total_gas_volume_l"
    assert result.total_gas_volume_l == pytest.approx(12.5)
    assert result.total_gas_volume_m3 == pytest.approx(liters_to_m3(12.5))
    assert result.gas_flow_rate_l_min is None
    assert result.exposure_duration_h is None
    assert result.vvm is None


def test_gas_flow_rate_plus_duration_mode_calculates_total_gas_volume() -> None:
    result = _estimate(
        total_gas_volume_l=None,
        gas_flow_rate_l_min=2.0,
        exposure_duration_h=3.0,
    )

    assert result.gas_exposure_mode == "gas_flow_rate_l_min_and_exposure_duration_h"
    assert result.gas_flow_rate_l_min == pytest.approx(2.0)
    assert result.exposure_duration_h == pytest.approx(3.0)
    assert result.total_gas_volume_l == pytest.approx(2.0 * 3.0 * 60.0)


def test_vvm_plus_duration_mode_calculates_flow_rate_and_total_gas_volume() -> None:
    result = _estimate(
        total_gas_volume_l=None,
        system_volume_l=10.0,
        vvm=0.2,
        exposure_duration_h=4.0,
    )

    assert result.gas_exposure_mode == "vvm_and_exposure_duration_h"
    assert result.gas_flow_rate_l_min == pytest.approx(0.2 * 10.0)
    assert result.total_gas_volume_l == pytest.approx(0.2 * 10.0 * 4.0 * 60.0)
    assert result.vvm == pytest.approx(0.2)


def test_mutually_exclusive_gas_exposure_modes_raise() -> None:
    with pytest.raises(ValueError, match="cannot be combined|exactly one"):
        _estimate(
            total_gas_volume_l=None,
            gas_flow_rate_l_min=1.0,
            exposure_duration_h=1.0,
            vvm=0.1,
        )


def test_total_gas_volume_cannot_be_combined_with_duration_or_flow_inputs() -> None:
    with pytest.raises(ValueError, match="total_gas_volume_l cannot be combined"):
        _estimate(total_gas_volume_l=1.0, exposure_duration_h=1.0)

    with pytest.raises(ValueError, match="total_gas_volume_l cannot be combined"):
        _estimate(total_gas_volume_l=1.0, gas_flow_rate_l_min=1.0)


def test_missing_duration_for_flow_rate_mode_raises() -> None:
    with pytest.raises(ValueError, match="requires exposure_duration_h"):
        _estimate(total_gas_volume_l=None, gas_flow_rate_l_min=1.0)


def test_missing_duration_for_vvm_mode_raises() -> None:
    with pytest.raises(ValueError, match="requires exposure_duration_h"):
        _estimate(total_gas_volume_l=None, vvm=0.1)


def test_event_count_equals_total_gas_volume_divided_by_spherical_bubble_volume() -> (
    None
):
    result = _estimate(total_gas_volume_l=2.0, bubble_radius_mm=0.5)
    radius_m = mm_to_m(0.5)
    expected_bubble_volume = (4.0 / 3.0) * math.pi * radius_m**3

    assert result.bubble_volume_m3 == pytest.approx(expected_bubble_volume)
    assert result.event_count == pytest.approx(
        liters_to_m3(2.0) / expected_bubble_volume
    )


def test_raw_viability_matches_equation_3_arithmetic() -> None:
    result = _estimate(
        system_volume_l=5.0,
        initial_viability_pct=90.0,
        single_event_viability_loss_pct=25.0,
        total_gas_volume_l=10.0,
        bubble_radius_mm=0.75,
    )
    expected_raw = 90.0 - (
        25.0 * result.event_count * result.affected_volume_m3 / result.system_volume_m3
    )

    assert result.raw_final_viability_pct == pytest.approx(expected_raw)


def test_clipping_below_zero_is_reported() -> None:
    result = _estimate(
        system_volume_l=0.001,
        initial_viability_pct=10.0,
        single_event_viability_loss_pct=100.0,
        total_gas_volume_l=1_000_000.0,
        bubble_radius_mm=0.1,
    )

    assert result.raw_final_viability_pct < 0.0
    assert result.final_viability_pct == pytest.approx(0.0)
    assert result.clipped is True
    assert "clipped" in " ".join(result.warnings)


def test_no_clipping_when_raw_value_is_in_range() -> None:
    result = _estimate(total_gas_volume_l=0.1, bubble_radius_mm=1.0)

    assert 0.0 <= result.raw_final_viability_pct <= 100.0
    assert result.final_viability_pct == pytest.approx(result.raw_final_viability_pct)
    assert result.clipped is False


def test_zero_gas_exposure_gives_zero_events_and_initial_viability() -> None:
    result = _estimate(total_gas_volume_l=0.0, initial_viability_pct=88.0)

    assert result.event_count == pytest.approx(0.0)
    assert result.raw_final_viability_pct == pytest.approx(88.0)
    assert result.final_viability_pct == pytest.approx(88.0)


def test_invalid_total_gas_volume_raises() -> None:
    for value in (-1.0, math.inf, math.nan, "not-a-number"):
        with pytest.raises(ValueError, match="total_gas_volume_l"):
            _estimate(total_gas_volume_l=value)


def test_invalid_gas_flow_rate_raises() -> None:
    for value in (-1.0, math.inf, math.nan):
        with pytest.raises(ValueError, match="gas_flow_rate_l_min"):
            _estimate(
                total_gas_volume_l=None,
                gas_flow_rate_l_min=value,
                exposure_duration_h=1.0,
            )


def test_invalid_vvm_raises() -> None:
    for value in (-1.0, math.inf, math.nan):
        with pytest.raises(ValueError, match="vvm"):
            _estimate(total_gas_volume_l=None, vvm=value, exposure_duration_h=1.0)


def test_invalid_exposure_duration_raises() -> None:
    for value in (-1.0, math.inf, math.nan):
        with pytest.raises(ValueError, match="exposure_duration_h"):
            _estimate(
                total_gas_volume_l=None,
                gas_flow_rate_l_min=1.0,
                exposure_duration_h=value,
            )


def test_invalid_system_volume_raises() -> None:
    for value in (0.0, -1.0, math.inf, math.nan, None):
        with pytest.raises(ValueError, match="system_volume_l"):
            _estimate(system_volume_l=value)


def test_invalid_initial_viability_raises() -> None:
    for value in (-1.0, 101.0, math.inf, math.nan, None):
        with pytest.raises(ValueError, match="initial_viability_pct"):
            _estimate(initial_viability_pct=value)


def test_invalid_single_event_viability_loss_raises() -> None:
    for value in (-1.0, 101.0, math.inf, math.nan, None):
        with pytest.raises(ValueError, match="single_event_viability_loss_pct"):
            _estimate(single_event_viability_loss_pct=value)


def test_invalid_user_supplied_bubble_radius_raises() -> None:
    for value in (0.0, -1.0, math.inf, math.nan, "not-a-number"):
        with pytest.raises(ValueError, match="bubble_radius_mm"):
            _estimate(bubble_radius_mm=value)


def test_out_of_domain_thread_radius_propagates_value_error() -> None:
    with pytest.raises(ValueError, match="thread_radius_um"):
        _estimate(thread_radius_um=9.9)


def test_out_of_domain_edr_threshold_propagates_value_error() -> None:
    with pytest.raises(ValueError, match="edr_threshold_w_m3"):
        _estimate(edr_threshold_w_m3=9.9e5)


def test_result_warnings_include_bounded_sensitivity_scope_terms() -> None:
    result = _estimate()
    warning_text = " ".join(result.warnings)
    assumption_text = " ".join(result.assumptions)

    assert "bounded" in warning_text
    assert "not a validated" in warning_text
    assert "process control" in warning_text
    assert "GMP" in warning_text
    assert "No automatic cell-line threshold" in warning_text
    assert "Figure 5a" in assumption_text
    assert "No rupture" in assumption_text


def test_inferred_bubble_radius_warnings_include_source_boundary_terms() -> None:
    result = _estimate(bubble_radius_mm=None)
    warning_text = " ".join(result.warnings)

    assert "Table 3" in warning_text
    assert "not measured" in warning_text
    assert "No extrapolation" in warning_text
    assert "not a general sparger bubble-size predictor" in warning_text


def test_source_provenance_distinguishes_user_and_inferred_bubble_radius() -> None:
    user_result = _estimate(bubble_radius_mm=1.0)
    inferred_result = _estimate(bubble_radius_mm=None)

    assert "caller-supplied bubble radius" in user_result.source_provenance
    assert (
        "McRae et al. 2024 Table 3 inferred calculator R_b interpolation"
        in inferred_result.source_provenance
    )


def test_vvm_mode_reports_constant_system_volume_assumption() -> None:
    result = _estimate(
        total_gas_volume_l=None,
        system_volume_l=10.0,
        vvm=0.2,
        exposure_duration_h=1.0,
    )

    assert "constant over the exposure duration" in " ".join(result.assumptions)
