from typing import Any, get_type_hints

import pytest

from thalmetis_edr.results import Table3ReproductionResult, Table3ValidationResult
from thalmetis_edr.tables import (
    mcrae_2024_table3_inputs,
    reproduce_table3,
    validate_table3_against_published,
)


def test_table3_stubs_return_structured_annotations() -> None:
    assert get_type_hints(mcrae_2024_table3_inputs)["return"] == dict[str, Any]
    assert get_type_hints(reproduce_table3)["return"] is Table3ReproductionResult
    assert (
        get_type_hints(validate_table3_against_published)["return"]
        is Table3ValidationResult
    )


def test_table3_inputs_are_placeholder_metadata() -> None:
    inputs = mcrae_2024_table3_inputs()

    assert inputs["source"] == "McRae et al. 2024 Table 3"
    assert inputs["model_context"] == "mcrae_2024_table3"


def test_table3_inputs_do_not_share_nested_mutable_metadata() -> None:
    inputs = mcrae_2024_table3_inputs()
    inputs["notes"].append("caller mutation")

    fresh_inputs = mcrae_2024_table3_inputs()

    assert "caller mutation" not in fresh_inputs["notes"]


def test_table3_reproduction_stubs_are_scaffold_only() -> None:
    with pytest.raises(NotImplementedError):
        reproduce_table3()

    with pytest.raises(NotImplementedError):
        validate_table3_against_published()
