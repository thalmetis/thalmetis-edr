from typing import get_type_hints

import pytest

from thalmetis_edr.results import ViabilityEstimate, ViabilitySensitivityResult
from thalmetis_edr.units import ml_to_m3, nl_to_m3, percent_to_fraction
from thalmetis_edr.viability import (
    estimate_viability_after_events,
    viability_sensitivity,
)


def test_viability_stubs_return_structured_annotations() -> None:
    assert (
        get_type_hints(estimate_viability_after_events)["return"]
        is ViabilityEstimate
    )
    assert get_type_hints(viability_sensitivity)["return"] is ViabilitySensitivityResult


def test_viability_sensitivity_remains_deferred() -> None:
    with pytest.raises(NotImplementedError):
        viability_sensitivity()


def test_estimate_viability_after_events_matches_microfluidic_worked_example() -> None:
    result = estimate_viability_after_events(
        affected_volume_m3=nl_to_m3(0.48),
        event_count=700_000,
        system_volume_m3=ml_to_m3(2.5),
        initial_viability_fraction=percent_to_fraction(83.0),
        single_event_viability_loss_fraction=percent_to_fraction(36.0),
    )

    assert result.final_viability == pytest.approx(0.781616, rel=1e-8)


def test_generic_equation_3_docstring_sets_boundary() -> None:
    docstring = estimate_viability_after_events.__doc__ or ""

    assert "first-class packaged v0.1 viability use" in docstring
    assert "user-composed exploratory" in docstring
    assert "not a universal" in docstring
