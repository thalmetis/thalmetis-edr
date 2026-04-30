"""Viability helpers for the bounded v0.1 McRae 2024 scope."""

from __future__ import annotations

from typing import Any

from thalmetis_edr.published.mcrae_2024 import (
    MCRAE_2024_EQ_3,
    MCRAE_2024_MODEL_CONTEXT,
)
from thalmetis_edr.results import ViabilityEstimate, ViabilitySensitivityResult
from thalmetis_edr.units import EVENT_COUNT, VIABILITY_FRACTION, VOLUME_M3


def estimate_viability_after_events(
    *,
    affected_volume_m3: float | None = None,
    event_count: int | float | None = None,
    system_volume_m3: float | None = None,
    initial_viability_fraction: float | None = None,
    single_event_viability_loss_fraction: float | None = None,
    source: str = MCRAE_2024_EQ_3,
    **inputs: Any,
) -> ViabilityEstimate:
    """Bounded generic McRae et al. 2024 Equation 3 helper.

    The first-class packaged v0.1 viability use is McRae 2024 pinch-off /
    Table 3 only. Use outside that context is a user-composed exploratory
    calculation, not a packaged validated model. This is not a universal
    viability predictor.
    """
    if (
        affected_volume_m3 is None
        or event_count is None
        or system_volume_m3 is None
        or initial_viability_fraction is None
        or single_event_viability_loss_fraction is None
    ):
        raise ValueError(
            "Provide affected_volume_m3, event_count, system_volume_m3, "
            "initial_viability_fraction, and single_event_viability_loss_fraction."
        )
    if affected_volume_m3 < 0.0 or event_count < 0.0 or system_volume_m3 <= 0.0:
        raise ValueError("Affected volume and event count must be non-negative.")

    viability_loss_fraction = (
        single_event_viability_loss_fraction
        * float(event_count)
        * affected_volume_m3
        / system_volume_m3
    )
    unclamped_final_viability = initial_viability_fraction - viability_loss_fraction
    final_viability = min(max(unclamped_final_viability, 0.0), 1.0)

    warnings: list[str] = []
    if final_viability != unclamped_final_viability:
        warnings.append("Final viability was clamped into the [0, 1] interval.")

    return ViabilityEstimate(
        final_viability=final_viability,
        units={
            "affected_volume_m3": VOLUME_M3,
            "event_count": EVENT_COUNT,
            "system_volume_m3": VOLUME_M3,
            "initial_viability_fraction": VIABILITY_FRACTION,
            "single_event_viability_loss_fraction": VIABILITY_FRACTION,
            "final_viability": VIABILITY_FRACTION,
        },
        inputs={
            "affected_volume_m3": affected_volume_m3,
            "event_count": float(event_count),
            "system_volume_m3": system_volume_m3,
            "initial_viability_fraction": initial_viability_fraction,
            "single_event_viability_loss_fraction": (
                single_event_viability_loss_fraction
            ),
            **inputs,
        },
        input_provenance={
            "affected_volume_m3": "caller",
            "event_count": "caller",
            "system_volume_m3": "caller",
            "initial_viability_fraction": "caller",
            "single_event_viability_loss_fraction": "caller",
        },
        source=source,
        assumptions={
            "equation": "Psi = Psi0 - DeltaPsi_n * Nevents * Vaffected / Vsystem"
        },
        notes=[
            "Implements McRae et al. 2024 Equation 3 in fraction space using SI inputs."
        ],
        warnings=warnings,
        model_context=MCRAE_2024_MODEL_CONTEXT,
        event_context="pinch_off",
    )


def viability_sensitivity(
    *,
    source: str = MCRAE_2024_EQ_3,
    **inputs: Any,
) -> ViabilitySensitivityResult:
    """Scaffold bounded sensitivity helper for structured result workflows."""
    raise NotImplementedError(
        "Viability sensitivity calculations are not implemented in the bounded "
        "v0.1 package."
    )
