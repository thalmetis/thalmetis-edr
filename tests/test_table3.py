from typing import Any, get_type_hints

import pandas as pd
import pytest

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
    inferred_radii = mcrae_2024_table3_inputs()["inferred_radii"]

    expected_figure5a = pd.DataFrame(
        [
            (10, 0.1953975249713808, 0.0908537026773536, 0.034307252148419315),
            (20, 0.8362886140608151, 0.3628211514028486, 0.07171971744845981),
            (50, 5.33482558584271, 1.1081922590524727, 0.20742598903636442),
            (80, 11.230812054158598, 1.8076088061464917, 0.4819390775606926),
            (100, 12.284237116483222, 2.523848673293887, 0.6467924157386947),
            (150, 19.888486408382363, 5.73056413576899, 0.9746163174905726),
            (200, 32.4625541954605, 9.580969741642129, 0.6812010452821038),
            (250, 47.682154, 11.810533, 0.627047),
            (400, 119.44790775113934, 16.937707299399907, 0.25327424058495557),
            (500, 169.694288, 6.260675, 0.782589),
            (750, 223.48449090488623, 1.94395077394081, 0.2356544948569414),
            (1000, 155.295906, 4.117629, 0.313212),
            (1250, 25.25407540591507, 2.197260411793135, 0.1938939654081627),
        ],
        columns=[
            "thread_radius_um",
            "affected_volume_1e6_nl",
            "affected_volume_1e7_nl",
            "affected_volume_1e8_nl",
        ],
    )
    expected_published = pd.DataFrame(
        [
            (10, 0.18, 0, 12, 67),
            (20, 0.28, 0, 12, 83),
            (50, 0.56, 0, 66, 94),
            (80, 0.83, 0, 83, 95),
            (100, 1.0, 33, 86, 97),
            (150, 1.4, 62, 89, 98),
            (200, 1.8, 70, 91, 99),
            (400, 3.2, 79, 97, 100),
            (750, 4.7, 88, 100, 100),
            (1250, 6.4, 100, 100, 100),
        ],
        columns=[
            "thread_radius_um",
            "published_bubble_radius_mm",
            "viability_1e6_pct",
            "viability_1e7_pct",
            "viability_1e8_pct",
        ],
    )
    expected_inferred_radii = pd.DataFrame(
        [
            (10, 0.18, 0.178461),
            (20, 0.28, 0.283134),
            (50, 0.56, 0.564231),
            (80, 0.83, 0.834377),
            (100, 1.0, 1.002721),
            (150, 1.4, 1.422314),
            (200, 1.8, 1.811312),
            (400, 3.2, 3.150869),
            (750, 4.7, 4.679123),
            (1250, 6.4, 6.449000),
        ],
        columns=[
            "thread_radius_um",
            "published_bubble_radius_mm",
            "inferred_bubble_radius_for_calculator_mm",
        ],
    )

    pd.testing.assert_frame_equal(
        figure5a, expected_figure5a, rtol=0.0, atol=1.0e-15
    )
    pd.testing.assert_frame_equal(
        published, expected_published, check_exact=True
    )
    pd.testing.assert_frame_equal(
        inferred_radii, expected_inferred_radii, rtol=0.0, atol=0.0
    )


def test_reproduce_table3_returns_expected_rounded_calculated_cells() -> None:
    result = reproduce_table3()
    calculated = result.calculated_dataframe[
        [
            "thread_radius_um",
            "calc_viability_1e6_pct_rounded",
            "calc_viability_1e7_pct_rounded",
            "calc_viability_1e8_pct_rounded",
            "clipped_1e6",
            "clipped_1e7",
            "clipped_1e8",
        ]
    ].reset_index(drop=True)

    expected = pd.DataFrame(
        [
            (10, 0, 12, 67, True, False, False),
            (20, 0, 12, 83, True, False, False),
            (50, 0, 66, 94, True, False, False),
            (80, 0, 83, 95, True, False, False),
            (100, 33, 86, 96, False, False, False),
            (150, 62, 89, 98, False, False, False),
            (200, 70, 91, 99, False, False, False),
            (400, 79, 97, 100, False, False, False),
            (750, 88, 100, 100, False, False, False),
            (1250, 99, 100, 100, False, False, False),
        ],
        columns=[
            "thread_radius_um",
            "calc_viability_1e6_pct_rounded",
            "calc_viability_1e7_pct_rounded",
            "calc_viability_1e8_pct_rounded",
            "clipped_1e6",
            "clipped_1e7",
            "clipped_1e8",
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
    assert result.missing_published_keys == []
    assert result.extra_published_keys == []
    assert result.duplicate_published_keys == []
    assert result.missing_calculated_keys == []
    assert result.extra_calculated_keys == []
    assert result.duplicate_calculated_keys == []
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
    assert result.clipped_cells
    assert {
        "thread_radius_um": 10,
        "edr_threshold_w_m3": 1.0e6,
        "clipped": True,
        "final_viability_fraction": 0.0,
        "final_viability_pct_rounded": 0,
    } in result.clipped_cells
    assert "Some Table 3 pathway cells were clipped" in result.warnings[-1]


def test_table3_results_mark_caller_overrides_in_input_provenance() -> None:
    overridden_thresholds = [1.0e6, 1.0e7, 1.0e8]
    result = validate_table3_against_published(
        system_volume_l=4000.0,
        initial_viability_pct=95.0,
        edr_thresholds_w_m3=overridden_thresholds,
    )

    assert result.inputs["system_volume_l"] == pytest.approx(4000.0)
    assert result.inputs["initial_viability_pct"] == pytest.approx(95.0)
    assert result.inputs["edr_thresholds_w_m3"] == overridden_thresholds
    assert result.input_provenance["system_volume_l"] == "caller override"
    assert result.input_provenance["initial_viability_pct"] == "caller override"
    assert result.input_provenance["edr_thresholds_w_m3"] == "caller override"
    assert result.input_provenance["total_gas_volume_l"] == (
        "McRae 2024 Table 3 metadata"
    )
    assert result.input_provenance["single_event_viability_loss_pct"] == (
        "McRae 2024 Table 3 metadata"
    )


def test_reproduce_table3_rejects_unsupported_threshold_overrides() -> None:
    with pytest.raises(ValueError, match="supports only the packaged thresholds"):
        reproduce_table3(edr_thresholds_w_m3=(1.0e6, 5.0e6, 1.0e8))


def test_validate_table3_rejects_unsupported_threshold_overrides() -> None:
    with pytest.raises(ValueError, match="supports only the packaged thresholds"):
        validate_table3_against_published(edr_thresholds_w_m3=(1.0e6, 5.0e6, 1.0e8))


def test_default_threshold_behavior_still_works() -> None:
    result = reproduce_table3()

    assert result.inputs["edr_thresholds_w_m3"] == [1.0e6, 1.0e7, 1.0e8]
    assert result.input_provenance["edr_thresholds_w_m3"] == (
        "McRae 2024 Table 3 metadata"
    )


def test_exact_default_threshold_override_is_deterministic_and_provenanced() -> None:
    result = reproduce_table3(edr_thresholds_w_m3=(1.0e6, 1.0e7, 1.0e8))

    assert result.inputs["edr_thresholds_w_m3"] == [1.0e6, 1.0e7, 1.0e8]
    assert result.input_provenance["edr_thresholds_w_m3"] == "caller override"


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


def test_validation_fails_explicitly_for_unmatched_comparison_keys() -> None:
    published = mcrae_2024_published_table3()
    published.loc[
        published["thread_radius_um"] == 50, "published_bubble_radius_mm"
    ] = 0.57

    result = validate_table3_against_published(published_table3=published)

    assert result.passed is False
    assert result.published_fixture_integrity_passed is False
    assert result.calculated_pathway_passed is False
    assert result.unexpected_mismatches == []
    assert result.missing_expected_mismatches == []
    assert result.missing_published_keys == [
        {
            "thread_radius_um": 50,
            "published_bubble_radius_mm": pytest.approx(0.56),
        }
    ]
    assert result.extra_published_keys == [
        {
            "thread_radius_um": 50,
            "published_bubble_radius_mm": pytest.approx(0.57),
        }
    ]
    assert result.missing_calculated_keys == []
    assert result.extra_calculated_keys == []
    comparison_rows = result.comparison_dataframe.loc[
        result.comparison_dataframe["thread_radius_um"] == 50,
        ["published_bubble_radius_mm", "comparison_row_status"],
    ]
    assert comparison_rows.to_dict(orient="records") == [
        {
            "published_bubble_radius_mm": pytest.approx(0.56),
            "comparison_row_status": "right_only",
        },
        {
            "published_bubble_radius_mm": pytest.approx(0.57),
            "comparison_row_status": "left_only",
        },
    ]
    assert (
        "Table 3 comparison keys did not align exactly between the published "
        "fixture and calculated pathway rows."
    ) in result.warnings


def test_validation_fails_when_published_fixture_is_missing_expected_key() -> None:
    published = mcrae_2024_published_table3()
    published = published[published["thread_radius_um"] != 50].reset_index(drop=True)

    result = validate_table3_against_published(published_table3=published)

    assert result.passed is False
    assert result.published_fixture_integrity_passed is False
    assert result.calculated_pathway_passed is False
    assert result.missing_published_keys == [
        {
            "thread_radius_um": 50,
            "published_bubble_radius_mm": pytest.approx(0.56),
        }
    ]
    assert result.extra_published_keys == []
    assert result.missing_calculated_keys == []
    assert result.extra_calculated_keys == []
    comparison_rows = result.comparison_dataframe.loc[
        result.comparison_dataframe["thread_radius_um"] == 50,
        ["published_bubble_radius_mm", "comparison_row_status"],
    ]
    assert comparison_rows.to_dict(orient="records") == [
        {
            "published_bubble_radius_mm": pytest.approx(0.56),
            "comparison_row_status": "right_only",
        }
    ]


def test_validation_fails_when_calculated_pathway_is_missing_expected_key() -> None:
    inferred_radii = mcrae_2024_table3_inputs()["inferred_radii"]
    inferred_radii = inferred_radii[
        inferred_radii["thread_radius_um"] != 50
    ].reset_index(drop=True)

    result = validate_table3_against_published(inferred_radii=inferred_radii)

    assert result.passed is False
    assert result.published_fixture_integrity_passed is True
    assert result.calculated_pathway_passed is False
    assert result.missing_published_keys == []
    assert result.extra_published_keys == []
    assert result.missing_calculated_keys == [
        {
            "thread_radius_um": 50,
            "published_bubble_radius_mm": pytest.approx(0.56),
        }
    ]
    assert result.extra_calculated_keys == []
    comparison_rows = result.comparison_dataframe.loc[
        result.comparison_dataframe["thread_radius_um"] == 50,
        ["published_bubble_radius_mm", "comparison_row_status"],
    ]
    assert comparison_rows.to_dict(orient="records") == [
        {
            "published_bubble_radius_mm": pytest.approx(0.56),
            "comparison_row_status": "left_only",
        }
    ]


def test_validation_fails_when_both_sides_are_missing_same_expected_key() -> None:
    published = mcrae_2024_published_table3()
    published = published[published["thread_radius_um"] != 50].reset_index(drop=True)
    inferred_radii = mcrae_2024_table3_inputs()["inferred_radii"]
    inferred_radii = inferred_radii[
        inferred_radii["thread_radius_um"] != 50
    ].reset_index(drop=True)

    result = validate_table3_against_published(
        published_table3=published,
        inferred_radii=inferred_radii,
    )

    assert result.passed is False
    assert result.published_fixture_integrity_passed is False
    assert result.calculated_pathway_passed is False
    expected_key = {
        "thread_radius_um": 50,
        "published_bubble_radius_mm": pytest.approx(0.56),
    }
    assert result.missing_published_keys == [expected_key]
    assert result.missing_calculated_keys == [expected_key]
    assert result.comparison_dataframe[
        result.comparison_dataframe["thread_radius_um"] == 50
    ].empty


def test_validation_fails_clearly_for_duplicate_published_key() -> None:
    published = mcrae_2024_published_table3()
    duplicate_row = published.loc[published["thread_radius_um"] == 50]
    published = pd.concat([published, duplicate_row], ignore_index=True)

    result = validate_table3_against_published(published_table3=published)

    assert result.passed is False
    assert result.published_fixture_integrity_passed is False
    assert result.calculated_pathway_passed is False
    assert result.duplicate_published_keys == [
        {
            "thread_radius_um": 50,
            "published_bubble_radius_mm": pytest.approx(0.56),
            "duplicate_count": 2,
        }
    ]
    assert result.missing_published_keys == []
    assert result.extra_published_keys == []
