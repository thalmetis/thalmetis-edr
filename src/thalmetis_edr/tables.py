"""McRae et al. 2024 Table 3 reproduction stubs."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from thalmetis_edr.published.mcrae_2024 import TABLE3_INPUT_PLACEHOLDERS
from thalmetis_edr.results import Table3ReproductionResult, Table3ValidationResult


def mcrae_2024_table3_inputs() -> dict[str, Any]:
    """Return placeholder metadata for future McRae 2024 Table 3 inputs."""
    return deepcopy(TABLE3_INPUT_PLACEHOLDERS)


def reproduce_table3(**inputs: Any) -> Table3ReproductionResult:
    """Scaffold canonical v0.1 packaged McRae 2024 Table 3 pathway."""
    raise NotImplementedError(
        "McRae et al. 2024 Table 3 reproduction is not implemented in the "
        "v0.1 scaffold PR."
    )


def validate_table3_against_published(**inputs: Any) -> Table3ValidationResult:
    """Scaffold validation against published McRae et al. 2024 Table 3."""
    raise NotImplementedError(
        "McRae et al. 2024 Table 3 validation is not implemented in the "
        "v0.1 scaffold PR."
    )
