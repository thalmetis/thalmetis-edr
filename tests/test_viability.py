from typing import get_type_hints

import pytest

from thalmetis_edr.results import ViabilityEstimate, ViabilitySensitivityResult
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


def test_viability_stubs_are_scaffold_only() -> None:
    with pytest.raises(NotImplementedError):
        estimate_viability_after_events()

    with pytest.raises(NotImplementedError):
        viability_sensitivity()


def test_generic_equation_3_docstring_sets_boundary() -> None:
    docstring = estimate_viability_after_events.__doc__ or ""

    assert "first-class packaged v0.1 viability use" in docstring
    assert "user-composed exploratory" in docstring
    assert "not a universal" in docstring
