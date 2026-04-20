"""Viability helper stubs for the v0.1 McRae 2024 scope."""

from __future__ import annotations

from typing import Any

from thalmetis_edr.published.mcrae_2024 import MCRAE_2024_EQ_3
from thalmetis_edr.results import ViabilityEstimate, ViabilitySensitivityResult


def estimate_viability_after_events(
    *,
    affected_volume_m3: float | None = None,
    event_count: int | float | None = None,
    source: str = MCRAE_2024_EQ_3,
    **inputs: Any,
) -> ViabilityEstimate:
    """Scaffold generic McRae et al. 2024 Equation 3 helper.

    The first-class packaged v0.1 viability use is McRae 2024 pinch-off /
    Table 3 only. Use outside that context is a user-composed exploratory
    calculation, not a packaged validated model. This is not a universal
    viability predictor.
    """
    raise NotImplementedError(
        "McRae et al. 2024 Equation 3 viability calculation is not implemented "
        "in the v0.1 scaffold PR."
    )


def viability_sensitivity(
    *,
    source: str = MCRAE_2024_EQ_3,
    **inputs: Any,
) -> ViabilitySensitivityResult:
    """Scaffold bounded sensitivity helper for structured result workflows."""
    raise NotImplementedError(
        "Viability sensitivity calculations are not implemented in the v0.1 "
        "scaffold PR."
    )
