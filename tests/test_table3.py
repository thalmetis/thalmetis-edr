from typing import Any, get_type_hints

import pandas as pd

from thalmetis_edr.results import Table3ReproductionResult, Table3ValidationResult
from thalmetis_edr.tables import (
    estimate_table3_from_figure5a_volumes,
    mcrae_2024_figure5a_volumes,
    mcrae_2024_published_table3,
    mcrae_2024_table3_inputs,
    reproduce_table3,
    validate_table3_against_published,
)


def test_table3_stubs_return_structured_annotations() -> None:
    assert get_type_hints(mcrae_2024_table3_inputs)["return"] == dict[str, Any]
    assert (
        get_type_hints(estimate_table3_from_figure5a_volumes)["return"]
        is Table3ReproductionResult
    )
    assert get_type_hints(reproduce_table3)["return"] is Table3ReproductionResult
    assert (
        get_type_hints(validate_table3_against_published)["return"]
        is Table3ValidationResult
    )


def test_table3_inputs_are_explicit_metadata_with_fresh_frames() -> None:
    inputs = mcrae_2024_table3_inputs()

    assert inputs["source"] == "McRae et al. 2024 Table 3"
    assert inputs["model_context"] == "mcrae_2024_table3"
    assert inputs["edr_thresholds_w_m3"] == [1.0e6, 1.0e7, 1.0e8]
    assert inputs["total_gas_volume_l"] == 1_152_000.0
    assert inputs["system_volume_l"] == 5000.0
    assert inputs["initial_viability_pct"] == 100.0
    assert inputs["single_event_viability_loss_pct"] == 100.0


def test_table3_inputs_do_not_share_nested_mutable_metadata() -> None:
    inputs = mcrae_2024_table3_inputs()
    inputs["notes"].append("caller mutation")
    inputs["figure5a_volumes"].loc[0, "affected_volume_1e6_nl"] = -1.0

    fresh_inputs = mcrae_2024_table3_inputs()

    assert "caller mutation" not in fresh_inputs["notes"]
    assert fresh_inputs["figure5a_volumes"].loc[0, "affected_volume_1e6_nl"] > 0.0


def test_figure5a_and_published_table_accessors_return_expected_values() -> None:
    figure5a = mcrae_2024_figure5a_volumes()
    published = mcrae_2024_published_table3()

    assert len(figure5a) == 13
    assert len(published) == 10
    assert (
        figure5a.loc[
            figure5a["thread_radius_um"] == 100, "affected_volume_1e8_nl"
        ].item()
        == 0.6467924157386947
    )
    assert (
        published.loc[
            published["thread_radius_um"] == 400, "viability_1e7_pct"
        ].item()
        == 97
    )


def test_reproduce_table3_returns_expected_rounded_calculated_cells() -> None:
    result = reproduce_table3()
    calculated = result.calculated_dataframe[
        [
            "thread_radius_um",
            "calc_viability_1e6_pct_rounded",
            "calc_viability_1e7_pct_rounded",
            "calc_viability_1e8_pct_rounded",
        ]
    ].reset_index(drop=True)

    expected = pd.DataFrame(
        [
            (10, 0, 12, 67),
            (20, 0, 12, 83),
            (50, 0, 66, 94),
            (80, 0, 83, 95),
            (100, 33, 86, 96),
            (150, 62, 89, 98),
            (200, 70, 91, 99),
            (400, 79, 97, 100),
            (750, 88, 100, 100),
            (1250, 99, 100, 100),
        ],
        columns=[
            "thread_radius_um",
            "calc_viability_1e6_pct_rounded",
            "calc_viability_1e7_pct_rounded",
            "calc_viability_1e8_pct_rounded",
        ],
    )

    pd.testing.assert_frame_equal(calculated, expected)


def test_validate_table3_against_published_reports_only_expected_residual_mismatches(
) -> None:
    result = validate_table3_against_published()

    assert result.passed is True
    assert result.published_fixture_integrity_passed is True
    assert result.calculated_pathway_passed is True
    assert result.unexpected_mismatches == []
    assert result.missing_expected_mismatches == []
    assert result.expected_residual_mismatches == [
        {
            "thread_radius_um": 100,
            "edr_threshold_w_m3": 1.0e8,
            "calculated_viability_pct_rounded": 96,
            "published_viability_pct": 97,
        },
        {
            "thread_radius_um": 1250,
            "edr_threshold_w_m3": 1.0e6,
            "calculated_viability_pct_rounded": 99,
            "published_viability_pct": 100,
        },
    ]


def test_validation_fails_for_unexpected_mismatch_changes() -> None:
    published = mcrae_2024_published_table3()
    published.loc[published["thread_radius_um"] == 50, "viability_1e8_pct"] = 93

    result = validate_table3_against_published(published_table3=published)

    assert result.passed is False
    assert result.published_fixture_integrity_passed is False
    assert result.calculated_pathway_passed is False
    assert result.unexpected_mismatches == [
        {
            "thread_radius_um": 50,
            "edr_threshold_w_m3": 1.0e8,
            "calculated_viability_pct_rounded": 94,
            "published_viability_pct": 93,
        }
    ]
