"""Bounded McRae 2024 pinch-off viability sensitivity estimates."""

from __future__ import annotations

import math

from thalmetis_edr.affected_volume import interpolate_pinchoff_affected_volume
from thalmetis_edr.bubble_radius import interpolate_table3_bubble_radius
from thalmetis_edr.bubbles import bubble_volume, event_count_from_gas_volume
from thalmetis_edr.published.mcrae_2024 import MCRAE_2024_EQ_3
from thalmetis_edr.results import PinchoffViabilityEstimate
from thalmetis_edr.units import liters_to_m3, mm_to_m

_BUBBLE_RADIUS_SOURCE_USER = "user_supplied"
_BUBBLE_RADIUS_SOURCE_INFERRED = "inferred_table3_interpolation"

_GAS_MODE_TOTAL = "total_gas_volume_l"
_GAS_MODE_FLOW_DURATION = "gas_flow_rate_l_min_and_exposure_duration_h"
_GAS_MODE_VVM_DURATION = "vvm_and_exposure_duration_h"

_BASE_ASSUMPTIONS = (
    (
        "This is a bounded sensitivity estimate, not a validated industrial "
        "viability prediction."
    ),
    (
        "The user supplies the EDR threshold and single-event viability-loss "
        "assumptions; no automatic cell-line threshold lookup is performed."
    ),
    (
        "Affected volume comes from the packaged McRae 2024 Figure 5a "
        "interpolation pathway."
    ),
    (
        "Bubble radius comes from user input or optional inferred Table 3 "
        "calculator R_b fallback; user-supplied bubble radius is preferred "
        "when available."
    ),
    (
        "No media, growth-phase, passage, Pluronic, repair dynamics, "
        "residence-time, gas uptake, gas production, kLa, OTR, or proprietary "
        "cell-line resilience model is included."
    ),
    (
        "No rupture, coalescence, path-history, or thesis Table 4.4 behavior "
        "is included."
    ),
)
_BASE_WARNINGS = (
    (
        "This API is a bounded pinch-off viability sensitivity estimate only; "
        "it is not a validated industrial viability predictor."
    ),
    (
        "This result is not process control, GMP release, process approval, "
        "transfer approval, or batch release."
    ),
    (
        "No automatic cell-line threshold inference, growth-phase rules, "
        "Pluronic correction, residence-time model, gas uptake, gas "
        "production, kLa, OTR, or proprietary resilience model is included."
    ),
)
_INFERRED_BUBBLE_RADIUS_ASSUMPTION = (
    "The bubble radius was inferred from the v0.1 Table 3 reconciliation "
    "calculator R_b interpolation, not measured bubble-size data."
)
_USER_BUBBLE_RADIUS_ASSUMPTION = (
    "Thread radius and bubble radius were treated as separate caller-supplied "
    "or model-input assumptions; the inferred Table 3 R_t-to-R_b relation was "
    "not enforced."
)
_VVM_ASSUMPTION = (
    "VVM mode treats system_volume_l as constant over the exposure duration."
)


def _ensure_finite_positive(value: float, name: str) -> float:
    numeric_value = float(value)
    if not math.isfinite(numeric_value) or numeric_value <= 0.0:
        raise ValueError(f"{name} must be finite and positive.")
    return numeric_value


def _ensure_finite_non_negative(value: float, name: str) -> float:
    numeric_value = float(value)
    if not math.isfinite(numeric_value) or numeric_value < 0.0:
        raise ValueError(f"{name} must be finite and non-negative.")
    return numeric_value


def _ensure_percent(value: float, name: str) -> float:
    numeric_value = float(value)
    if not math.isfinite(numeric_value) or not 0.0 <= numeric_value <= 100.0:
        raise ValueError(f"{name} must be finite and between 0 and 100 inclusive.")
    return numeric_value


def _resolve_gas_exposure(
    *,
    total_gas_volume_l: float | None,
    gas_flow_rate_l_min: float | None,
    exposure_duration_h: float | None,
    vvm: float | None,
    system_volume_l: float,
) -> tuple[str, float, float | None, float | None, float | None]:
    has_total = total_gas_volume_l is not None
    has_flow = gas_flow_rate_l_min is not None
    has_duration = exposure_duration_h is not None
    has_vvm = vvm is not None

    if has_total:
        if has_flow or has_vvm or has_duration:
            raise ValueError(
                "total_gas_volume_l cannot be combined with gas_flow_rate_l_min, "
                "vvm, or exposure_duration_h."
            )
        total = _ensure_finite_non_negative(total_gas_volume_l, "total_gas_volume_l")
        return (_GAS_MODE_TOTAL, total, None, None, None)

    if has_flow:
        if has_vvm:
            raise ValueError("gas_flow_rate_l_min cannot be combined with vvm.")
        if not has_duration:
            raise ValueError("gas_flow_rate_l_min requires exposure_duration_h.")
        flow = _ensure_finite_non_negative(gas_flow_rate_l_min, "gas_flow_rate_l_min")
        duration = _ensure_finite_non_negative(
            exposure_duration_h, "exposure_duration_h"
        )
        total = flow * duration * 60.0
        return (_GAS_MODE_FLOW_DURATION, total, flow, duration, None)

    if has_vvm:
        if not has_duration:
            raise ValueError("vvm requires exposure_duration_h.")
        resolved_vvm = _ensure_finite_non_negative(vvm, "vvm")
        duration = _ensure_finite_non_negative(
            exposure_duration_h, "exposure_duration_h"
        )
        flow = resolved_vvm * system_volume_l
        total = resolved_vvm * system_volume_l * duration * 60.0
        return (_GAS_MODE_VVM_DURATION, total, flow, duration, resolved_vvm)

    if has_duration:
        raise ValueError(
            "exposure_duration_h requires gas_flow_rate_l_min or vvm unless "
            "total_gas_volume_l is used alone."
        )
    raise ValueError(
        "Specify exactly one gas exposure mode: total_gas_volume_l, "
        "gas_flow_rate_l_min with exposure_duration_h, or vvm with "
        "exposure_duration_h."
    )


def _resolve_bubble_radius(
    *,
    bubble_radius_mm: float | None,
    thread_radius_um: float,
    use_inferred_bubble_radius: bool,
) -> tuple[float, float, str, object | None, tuple[str, ...], tuple[str, ...]]:
    if bubble_radius_mm is not None:
        radius_mm = _ensure_finite_positive(bubble_radius_mm, "bubble_radius_mm")
        return (
            radius_mm,
            mm_to_m(radius_mm),
            _BUBBLE_RADIUS_SOURCE_USER,
            None,
            (_USER_BUBBLE_RADIUS_ASSUMPTION,),
            ("caller-supplied bubble radius",),
        )

    if not use_inferred_bubble_radius:
        raise ValueError(
            "bubble_radius_mm is required when use_inferred_bubble_radius is False."
        )

    estimate = interpolate_table3_bubble_radius(thread_radius_um)
    return (
        estimate.bubble_radius_mm,
        estimate.bubble_radius_m,
        _BUBBLE_RADIUS_SOURCE_INFERRED,
        estimate.metadata,
        (*estimate.assumptions, _INFERRED_BUBBLE_RADIUS_ASSUMPTION),
        ("McRae et al. 2024 Table 3 inferred calculator R_b interpolation",),
    )


def estimate_pinchoff_viability(
    *,
    thread_radius_um: float,
    edr_threshold_w_m3: float,
    system_volume_l: float,
    initial_viability_pct: float,
    single_event_viability_loss_pct: float,
    total_gas_volume_l: float | None = None,
    gas_flow_rate_l_min: float | None = None,
    exposure_duration_h: float | None = None,
    vvm: float | None = None,
    bubble_radius_mm: float | None = None,
    use_inferred_bubble_radius: bool = True,
) -> PinchoffViabilityEstimate:
    """Estimate bounded pinch-off viability sensitivity using McRae Eq. 3."""
    resolved_system_volume_l = _ensure_finite_positive(
        system_volume_l, "system_volume_l"
    )
    resolved_initial_viability_pct = _ensure_percent(
        initial_viability_pct, "initial_viability_pct"
    )
    resolved_single_event_loss_pct = _ensure_percent(
        single_event_viability_loss_pct, "single_event_viability_loss_pct"
    )

    affected_volume = interpolate_pinchoff_affected_volume(
        thread_radius_um, edr_threshold_w_m3
    )
    (
        resolved_bubble_radius_mm,
        resolved_bubble_radius_m,
        bubble_radius_source,
        bubble_radius_metadata,
        bubble_radius_assumptions,
        bubble_radius_provenance,
    ) = _resolve_bubble_radius(
        bubble_radius_mm=bubble_radius_mm,
        thread_radius_um=affected_volume.thread_radius_um,
        use_inferred_bubble_radius=use_inferred_bubble_radius,
    )
    (
        gas_exposure_mode,
        resolved_total_gas_volume_l,
        resolved_gas_flow_rate_l_min,
        resolved_exposure_duration_h,
        resolved_vvm,
    ) = _resolve_gas_exposure(
        total_gas_volume_l=total_gas_volume_l,
        gas_flow_rate_l_min=gas_flow_rate_l_min,
        exposure_duration_h=exposure_duration_h,
        vvm=vvm,
        system_volume_l=resolved_system_volume_l,
    )

    total_gas_volume_m3 = liters_to_m3(resolved_total_gas_volume_l)
    system_volume_m3 = liters_to_m3(resolved_system_volume_l)
    bubble_result = bubble_volume(bubble_radius_m=resolved_bubble_radius_m)
    event_result = event_count_from_gas_volume(
        cumulative_gas_volume_m3=total_gas_volume_m3,
        bubble_volume_m3=bubble_result.bubble_volume_m3,
    )
    event_count = float(event_result.event_count)

    raw_final_viability_pct = resolved_initial_viability_pct - (
        resolved_single_event_loss_pct
        * event_count
        * affected_volume.affected_volume_m3
        / system_volume_m3
    )
    final_viability_pct = min(max(raw_final_viability_pct, 0.0), 100.0)
    clipped = final_viability_pct != raw_final_viability_pct

    assumptions = (
        *_BASE_ASSUMPTIONS,
        *affected_volume.assumptions,
        *bubble_radius_assumptions,
    )
    if gas_exposure_mode == _GAS_MODE_VVM_DURATION:
        assumptions = (*assumptions, _VVM_ASSUMPTION)

    warnings = (
        *_BASE_WARNINGS,
        *affected_volume.warnings,
    )
    if bubble_radius_source == _BUBBLE_RADIUS_SOURCE_INFERRED:
        warnings = (
            *warnings,
            "Inferred Table 3 R_b is not measured bubble-size data.",
        )
    if clipped:
        warnings = (
            *warnings,
            "Final viability was clipped into the [0, 100] percent interval.",
        )

    source_provenance = (
        "McRae et al. 2024 Figure 5a affected-volume interpolation",
        *bubble_radius_provenance,
        f"{MCRAE_2024_EQ_3} viability arithmetic",
        "cumulative gas volume / spherical bubble volume event count",
    )

    return PinchoffViabilityEstimate(
        final_viability_pct=final_viability_pct,
        raw_final_viability_pct=raw_final_viability_pct,
        clipped=clipped,
        initial_viability_pct=resolved_initial_viability_pct,
        single_event_viability_loss_pct=resolved_single_event_loss_pct,
        thread_radius_um=affected_volume.thread_radius_um,
        edr_threshold_w_m3=affected_volume.edr_threshold_w_m3,
        affected_volume_nl=affected_volume.affected_volume_nl,
        affected_volume_m3=affected_volume.affected_volume_m3,
        bubble_radius_mm=resolved_bubble_radius_mm,
        bubble_radius_m=resolved_bubble_radius_m,
        bubble_radius_source=bubble_radius_source,
        bubble_volume_m3=bubble_result.bubble_volume_m3,
        gas_exposure_mode=gas_exposure_mode,
        total_gas_volume_l=resolved_total_gas_volume_l,
        total_gas_volume_m3=total_gas_volume_m3,
        gas_flow_rate_l_min=resolved_gas_flow_rate_l_min,
        exposure_duration_h=resolved_exposure_duration_h,
        vvm=resolved_vvm,
        system_volume_l=resolved_system_volume_l,
        system_volume_m3=system_volume_m3,
        event_count=event_count,
        affected_volume_metadata=affected_volume.metadata,
        bubble_radius_metadata=bubble_radius_metadata,
        assumptions=assumptions,
        warnings=warnings,
        source_provenance=source_provenance,
    )
