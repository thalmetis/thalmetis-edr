"""McRae et al. 2024 Figure 5a and Table 3 pathway helpers."""

from __future__ import annotations

import math
from copy import deepcopy
from functools import lru_cache
from importlib.resources import files
from io import StringIO
from typing import Any

import pandas as pd

from thalmetis_edr.bubbles import bubble_volume, event_count_from_gas_volume
from thalmetis_edr.published.mcrae_2024 import (
    MCRAE_2024_EQ_3,
    MCRAE_2024_FIGURE5A_VOLUME_FILENAME,
    MCRAE_2024_TABLE3_CONTEXT,
    MCRAE_2024_TABLE3_INFERRED_RADII_FILENAME,
    MCRAE_2024_TABLE3_KNOWN_RESIDUAL_MISMATCHES,
    MCRAE_2024_TABLE3_PATHWAY_METADATA,
    MCRAE_2024_TABLE3_PUBLISHED_FILENAME,
    MCRAE_2024_TABLE_3,
)
from thalmetis_edr.results import Table3ReproductionResult, Table3ValidationResult
from thalmetis_edr.units import (
    ENERGY_DISSIPATION_RATE_W_M3,
    EVENT_COUNT,
    LENGTH_M,
    VIABILITY_FRACTION,
    VIABILITY_PERCENT,
    VOLUME_M3,
    liters_to_m3,
    mm_to_m,
    nl_to_m3,
    percent_to_fraction,
)
from thalmetis_edr.viability import estimate_viability_after_events

_THRESHOLD_COLUMN_SPECS: tuple[tuple[float, str, str], ...] = (
    (1.0e6, "affected_volume_1e6_nl", "viability_1e6_pct"),
    (1.0e7, "affected_volume_1e7_nl", "viability_1e7_pct"),
    (1.0e8, "affected_volume_1e8_nl", "viability_1e8_pct"),
)
_TABLE3_KEY_COLUMNS: tuple[str, str] = (
    "thread_radius_um",
    "published_bubble_radius_mm",
)
_PATHWAY_INPUT_PROVENANCE_FIELDS: tuple[str, ...] = (
    "edr_thresholds_w_m3",
    "total_gas_volume_l",
    "system_volume_l",
    "initial_viability_pct",
    "single_event_viability_loss_pct",
)
_PACKAGE_METADATA_PROVENANCE = "McRae 2024 Table 3 metadata"
_CALLER_OVERRIDE_PROVENANCE = "caller override"
_SUPPORTED_TABLE3_THRESHOLDS_W_M3 = tuple(spec[0] for spec in _THRESHOLD_COLUMN_SPECS)


def _threshold_suffix(threshold: float) -> str:
    return f"1e{int(round(math.log10(threshold)))}"


def _normalise_supported_thresholds(raw_thresholds: Any) -> tuple[float, float, float]:
    try:
        thresholds = tuple(float(value) for value in raw_thresholds)
    except TypeError as exc:
        raise ValueError(
            "The McRae 2024 Table 3 pathway supports only the packaged "
            "thresholds 1e6, 1e7, and 1e8 W/m^3. For arbitrary threshold "
            "analyses, call estimate_viability_after_events(...) with "
            "user-supplied affected volume."
        ) from exc

    if thresholds != _SUPPORTED_TABLE3_THRESHOLDS_W_M3:
        raise ValueError(
            "The McRae 2024 Table 3 pathway supports only the packaged "
            "thresholds 1e6, 1e7, and 1e8 W/m^3. For arbitrary threshold "
            "analyses, call estimate_viability_after_events(...) with "
            "user-supplied affected volume."
        )
    return thresholds


@lru_cache
def _load_packaged_csv(filename: str) -> pd.DataFrame:
    csv_text = (
        files("thalmetis_edr")
        .joinpath("data")
        .joinpath(filename)
        .read_text(encoding="utf-8")
    )
    return pd.read_csv(StringIO(csv_text))


def _copy_frame(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.copy(deep=True)


def mcrae_2024_figure5a_volumes() -> pd.DataFrame:
    """Return packaged Figure 5a affected-volume data."""
    return _copy_frame(_load_packaged_csv(MCRAE_2024_FIGURE5A_VOLUME_FILENAME))


def mcrae_2024_published_table3() -> pd.DataFrame:
    """Return packaged published Table 3 values exactly as displayed."""
    return _copy_frame(_load_packaged_csv(MCRAE_2024_TABLE3_PUBLISHED_FILENAME))


def _mcrae_2024_inferred_table3_radii() -> pd.DataFrame:
    return _copy_frame(_load_packaged_csv(MCRAE_2024_TABLE3_INFERRED_RADII_FILENAME))


def mcrae_2024_table3_inputs() -> dict[str, Any]:
    """Return explicit inputs for the packaged McRae 2024 Table 3 pathway."""
    metadata = deepcopy(MCRAE_2024_TABLE3_PATHWAY_METADATA)
    metadata["figure5a_volumes"] = mcrae_2024_figure5a_volumes()
    metadata["published_table3"] = mcrae_2024_published_table3()
    metadata["inferred_radii"] = _mcrae_2024_inferred_table3_radii()
    return metadata


def _resolve_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    resolved = mcrae_2024_table3_inputs()
    resolved.update(inputs)
    if "edr_thresholds_w_m3" in inputs:
        resolved["edr_thresholds_w_m3"] = list(
            _normalise_supported_thresholds(inputs["edr_thresholds_w_m3"])
        )
    resolved["figure5a_volumes"] = _copy_frame(resolved["figure5a_volumes"])
    resolved["published_table3"] = _copy_frame(resolved["published_table3"])
    resolved["inferred_radii"] = _copy_frame(resolved["inferred_radii"])
    resolved["_pathway_input_provenance"] = {
        field: (
            _CALLER_OVERRIDE_PROVENANCE
            if field in inputs
            else _PACKAGE_METADATA_PROVENANCE
        )
        for field in _PATHWAY_INPUT_PROVENANCE_FIELDS
    }
    return resolved


def _normalise_expected_mismatches() -> list[dict[str, Any]]:
    return [dict(item) for item in MCRAE_2024_TABLE3_KNOWN_RESIDUAL_MISMATCHES]


def _normalise_key(
    thread_radius_um: Any, published_bubble_radius_mm: Any
) -> tuple[int, float]:
    return (int(thread_radius_um), float(published_bubble_radius_mm))


def _key_records_from_dataframe(frame: pd.DataFrame) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in frame.loc[:, list(_TABLE3_KEY_COLUMNS)].to_dict(orient="records"):
        records.append(
            {
                "thread_radius_um": int(row["thread_radius_um"]),
                "published_bubble_radius_mm": float(row["published_bubble_radius_mm"]),
            }
        )
    return records


def _sorted_key_records_from_set(
    key_set: set[tuple[int, float]],
) -> list[dict[str, Any]]:
    return [
        {
            "thread_radius_um": thread_radius_um,
            "published_bubble_radius_mm": published_bubble_radius_mm,
        }
        for thread_radius_um, published_bubble_radius_mm in sorted(key_set)
    ]


def _key_set(frame: pd.DataFrame) -> set[tuple[int, float]]:
    return {
        _normalise_key(row["thread_radius_um"], row["published_bubble_radius_mm"])
        for row in frame.loc[:, list(_TABLE3_KEY_COLUMNS)].to_dict(orient="records")
    }


def _duplicate_key_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    duplicate_counts = (
        frame.groupby(list(_TABLE3_KEY_COLUMNS), dropna=False)
        .size()
        .reset_index(name="duplicate_count")
    )
    duplicates = duplicate_counts[duplicate_counts["duplicate_count"] > 1]
    records: list[dict[str, Any]] = []
    for row in duplicates.to_dict(orient="records"):
        records.append(
            {
                "thread_radius_um": int(row["thread_radius_um"]),
                "published_bubble_radius_mm": float(row["published_bubble_radius_mm"]),
                "duplicate_count": int(row["duplicate_count"]),
            }
        )
    return records


def _canonical_expected_table3_keys() -> list[dict[str, Any]]:
    return _key_records_from_dataframe(mcrae_2024_published_table3())


def _assess_table3_key_completeness(
    published_table3: pd.DataFrame, calculated_table3: pd.DataFrame
) -> dict[str, list[dict[str, Any]]]:
    expected_key_set = {
        _normalise_key(record["thread_radius_um"], record["published_bubble_radius_mm"])
        for record in _canonical_expected_table3_keys()
    }
    published_key_set = _key_set(published_table3)
    calculated_key_set = _key_set(calculated_table3)

    return {
        "missing_published_keys": _sorted_key_records_from_set(
            expected_key_set - published_key_set
        ),
        "extra_published_keys": _sorted_key_records_from_set(
            published_key_set - expected_key_set
        ),
        "duplicate_published_keys": _duplicate_key_records(published_table3),
        "missing_calculated_keys": _sorted_key_records_from_set(
            expected_key_set - calculated_key_set
        ),
        "extra_calculated_keys": _sorted_key_records_from_set(
            calculated_key_set - expected_key_set
        ),
        "duplicate_calculated_keys": _duplicate_key_records(calculated_table3),
    }


def _extract_clipped_cells(calculated_table3: pd.DataFrame) -> list[dict[str, Any]]:
    clipped_cells: list[dict[str, Any]] = []
    for row in calculated_table3.to_dict(orient="records"):
        for threshold, _affected_column, _published_column in _THRESHOLD_COLUMN_SPECS:
            suffix = _threshold_suffix(threshold)
            clipped_value = bool(row[f"clipped_{suffix}"])
            if clipped_value:
                clipped_cells.append(
                    {
                        "thread_radius_um": int(row["thread_radius_um"]),
                        "edr_threshold_w_m3": threshold,
                        "clipped": True,
                        "final_viability_fraction": float(
                            row[f"calc_viability_{suffix}_fraction"]
                        ),
                        "final_viability_pct_rounded": int(
                            row[f"calc_viability_{suffix}_pct_rounded"]
                        ),
                    }
                )
    return clipped_cells


def _calculate_table3_dataframe(resolved: dict[str, Any]) -> pd.DataFrame:
    figure5a_volumes = resolved["figure5a_volumes"]
    inferred_radii = resolved["inferred_radii"]

    merged = inferred_radii.merge(
        figure5a_volumes,
        on="thread_radius_um",
        how="inner",
    )

    total_gas_volume_m3 = liters_to_m3(float(resolved["total_gas_volume_l"]))
    system_volume_m3 = liters_to_m3(float(resolved["system_volume_l"]))
    initial_viability_fraction = percent_to_fraction(
        float(resolved["initial_viability_pct"])
    )
    single_event_viability_loss_fraction = percent_to_fraction(
        float(resolved["single_event_viability_loss_pct"])
    )

    calculated_rows: list[dict[str, Any]] = []
    for row in merged.to_dict(orient="records"):
        bubble_radius_m = mm_to_m(
            float(row["inferred_bubble_radius_for_calculator_mm"])
        )
        bubble_result = bubble_volume(bubble_radius_m=bubble_radius_m)
        event_count_result = event_count_from_gas_volume(
            cumulative_gas_volume_m3=total_gas_volume_m3,
            bubble_volume_m3=bubble_result.bubble_volume_m3,
        )

        calculated_row: dict[str, Any] = {
            "thread_radius_um": int(row["thread_radius_um"]),
            "published_bubble_radius_mm": float(row["published_bubble_radius_mm"]),
            "inferred_bubble_radius_for_calculator_mm": float(
                row["inferred_bubble_radius_for_calculator_mm"]
            ),
            "bubble_radius_m": bubble_radius_m,
            "bubble_volume_m3": bubble_result.bubble_volume_m3,
            "bubble_volume_nl": bubble_result.bubble_volume_m3 / 1.0e-12,
            "cumulative_gas_volume_m3": total_gas_volume_m3,
            "system_volume_m3": system_volume_m3,
            "event_count": event_count_result.event_count,
            "initial_viability_fraction": initial_viability_fraction,
            "single_event_viability_loss_fraction": (
                single_event_viability_loss_fraction
            ),
        }

        for threshold, affected_column, _published_column in _THRESHOLD_COLUMN_SPECS:
            viability_result = estimate_viability_after_events(
                affected_volume_m3=nl_to_m3(float(row[affected_column])),
                event_count=event_count_result.event_count,
                system_volume_m3=system_volume_m3,
                initial_viability_fraction=initial_viability_fraction,
                single_event_viability_loss_fraction=(
                    single_event_viability_loss_fraction
                ),
                source=MCRAE_2024_EQ_3,
                edr_threshold_w_m3=threshold,
            )
            suffix = _threshold_suffix(threshold)
            calculated_row[f"affected_volume_{suffix}_nl"] = float(row[affected_column])
            calculated_row[f"calc_viability_{suffix}_fraction"] = (
                viability_result.final_viability
            )
            calculated_row[f"calc_viability_{suffix}_pct"] = (
                viability_result.final_viability * 100.0
            )
            calculated_row[f"calc_viability_{suffix}_pct_rounded"] = int(
                round(viability_result.final_viability * 100.0)
            )
            calculated_row[f"clipped_{suffix}"] = bool(viability_result.warnings)

        calculated_rows.append(calculated_row)

    return (
        pd.DataFrame(calculated_rows)
        .sort_values("thread_radius_um")
        .reset_index(drop=True)
    )


def _build_comparison_dataframe(
    published_table3: pd.DataFrame, calculated_table3: pd.DataFrame
) -> pd.DataFrame:
    comparison = published_table3.merge(
        calculated_table3,
        on=list(_TABLE3_KEY_COLUMNS),
        how="outer",
        indicator=True,
    )
    comparison = comparison.rename(columns={"_merge": "comparison_row_status"})
    for threshold, _affected_column, published_column in _THRESHOLD_COLUMN_SPECS:
        suffix = _threshold_suffix(threshold)
        comparison[f"viability_delta_{suffix}_pct_points"] = (
            comparison[f"calc_viability_{suffix}_pct_rounded"]
            - comparison[published_column]
        )
    return comparison.sort_values(
        ["thread_radius_um", "published_bubble_radius_mm"]
    ).reset_index(drop=True)


def _extract_mismatch_cells(comparison: pd.DataFrame) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []
    for row in comparison.to_dict(orient="records"):
        if row.get("comparison_row_status") != "both":
            continue
        for threshold, _affected_column, published_column in _THRESHOLD_COLUMN_SPECS:
            suffix = _threshold_suffix(threshold)
            calculated_value = int(row[f"calc_viability_{suffix}_pct_rounded"])
            published_value = int(row[published_column])
            if calculated_value != published_value:
                mismatches.append(
                    {
                        "thread_radius_um": int(row["thread_radius_um"]),
                        "edr_threshold_w_m3": threshold,
                        "calculated_viability_pct_rounded": calculated_value,
                        "published_viability_pct": published_value,
                    }
                )
    return mismatches


def _same_mismatch_cell(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        int(left["thread_radius_um"]) == int(right["thread_radius_um"])
        and float(left["edr_threshold_w_m3"]) == float(right["edr_threshold_w_m3"])
        and int(left["calculated_viability_pct_rounded"])
        == int(right["calculated_viability_pct_rounded"])
        and int(left["published_viability_pct"])
        == int(right["published_viability_pct"])
    )


def _dataframes_match(left: pd.DataFrame, right: pd.DataFrame) -> bool:
    left_sorted = left.sort_values(list(left.columns)).reset_index(drop=True)
    right_sorted = right.sort_values(list(right.columns)).reset_index(drop=True)
    return left_sorted.equals(right_sorted)


def _validate_table3(
    *,
    resolved: dict[str, Any],
    published_table3: pd.DataFrame,
    calculated_table3: pd.DataFrame,
    comparison: pd.DataFrame,
) -> Table3ValidationResult:
    packaged_published = mcrae_2024_published_table3()
    published_fixture_integrity_passed = _dataframes_match(
        published_table3, packaged_published
    )

    key_completeness = _assess_table3_key_completeness(
        published_table3, calculated_table3
    )
    expected_mismatches = _normalise_expected_mismatches()
    actual_mismatches = _extract_mismatch_cells(comparison)
    clipped_cells = _extract_clipped_cells(calculated_table3)
    expected_residual_mismatches = [
        mismatch
        for mismatch in actual_mismatches
        if any(
            _same_mismatch_cell(mismatch, expected) for expected in expected_mismatches
        )
    ]
    unexpected_mismatches = [
        mismatch
        for mismatch in actual_mismatches
        if not any(
            _same_mismatch_cell(mismatch, expected) for expected in expected_mismatches
        )
    ]
    missing_expected_mismatches = [
        expected
        for expected in expected_mismatches
        if not any(
            _same_mismatch_cell(expected, actual) for actual in actual_mismatches
        )
    ]

    calculated_pathway_passed = (
        not key_completeness["missing_published_keys"]
        and not key_completeness["extra_published_keys"]
        and not key_completeness["duplicate_published_keys"]
        and not key_completeness["missing_calculated_keys"]
        and not key_completeness["extra_calculated_keys"]
        and not key_completeness["duplicate_calculated_keys"]
        and not unexpected_mismatches
        and not missing_expected_mismatches
    )
    passed = published_fixture_integrity_passed and calculated_pathway_passed

    warnings: list[str] = []
    for mismatch in expected_residual_mismatches:
        warnings.append(
            "Expected residual mismatch at "
            f"{mismatch['thread_radius_um']} um / "
            f"{_threshold_suffix(float(mismatch['edr_threshold_w_m3']))} W/m^3: "
            f"calculated {mismatch['calculated_viability_pct_rounded']}%, "
            f"published {mismatch['published_viability_pct']}%."
        )
    if unexpected_mismatches:
        warnings.append("Unexpected Table 3 mismatches were detected.")
    if missing_expected_mismatches:
        warnings.append("Expected residual mismatches were not found as expected.")
    if key_completeness["missing_published_keys"]:
        warnings.append("Expected published Table 3 keys were missing.")
    if key_completeness["extra_published_keys"]:
        warnings.append("Unexpected published Table 3 keys were present.")
    if key_completeness["duplicate_published_keys"]:
        warnings.append("Duplicate published Table 3 keys were detected.")
    if key_completeness["missing_calculated_keys"]:
        warnings.append("Expected calculated Table 3 keys were missing.")
    if key_completeness["extra_calculated_keys"]:
        warnings.append("Unexpected calculated Table 3 keys were present.")
    if key_completeness["duplicate_calculated_keys"]:
        warnings.append("Duplicate calculated Table 3 keys were detected.")
    if comparison["comparison_row_status"].ne("both").any():
        warnings.append(
            "Table 3 comparison keys did not align exactly between the "
            "published fixture and calculated pathway rows."
        )
    if clipped_cells:
        warnings.append(
            "Some Table 3 pathway cells were clipped into the [0, 1] "
            "viability interval."
        )

    return Table3ValidationResult(
        passed=passed,
        dataframe=_copy_frame(comparison),
        published_dataframe=_copy_frame(published_table3),
        calculated_dataframe=_copy_frame(calculated_table3),
        comparison_dataframe=_copy_frame(comparison),
        published_fixture_integrity_passed=published_fixture_integrity_passed,
        calculated_pathway_passed=calculated_pathway_passed,
        expected_residual_mismatches=expected_residual_mismatches,
        unexpected_mismatches=unexpected_mismatches,
        missing_expected_mismatches=missing_expected_mismatches,
        missing_published_keys=key_completeness["missing_published_keys"],
        extra_published_keys=key_completeness["extra_published_keys"],
        duplicate_published_keys=key_completeness["duplicate_published_keys"],
        missing_calculated_keys=key_completeness["missing_calculated_keys"],
        extra_calculated_keys=key_completeness["extra_calculated_keys"],
        duplicate_calculated_keys=key_completeness["duplicate_calculated_keys"],
        clipped_cells=clipped_cells,
        units={
            "edr_threshold_w_m3": ENERGY_DISSIPATION_RATE_W_M3,
            "bubble_radius_m": LENGTH_M,
            "bubble_volume_m3": VOLUME_M3,
            "event_count": EVENT_COUNT,
            "calc_viability_fraction": VIABILITY_FRACTION,
            "calc_viability_pct_rounded": VIABILITY_PERCENT,
            "clipped": "boolean",
        },
        inputs={
            "edr_thresholds_w_m3": list(resolved["edr_thresholds_w_m3"]),
            "total_gas_volume_l": resolved["total_gas_volume_l"],
            "system_volume_l": resolved["system_volume_l"],
            "initial_viability_pct": resolved["initial_viability_pct"],
            "single_event_viability_loss_pct": (
                resolved["single_event_viability_loss_pct"]
            ),
        },
        input_provenance={
            field: resolved["_pathway_input_provenance"][field]
            for field in _PATHWAY_INPUT_PROVENANCE_FIELDS
        },
        source=MCRAE_2024_TABLE_3,
        assumptions=deepcopy(resolved["assumptions"]),
        notes=[
            (
                "Published fixture integrity must match the packaged Table 3 source "
                "exactly."
            ),
            (
                "Calculated pathway passes only when mismatches equal the two known "
                "expected residual cells."
            ),
        ],
        warnings=warnings,
        model_context=MCRAE_2024_TABLE3_CONTEXT,
        event_context="pinch_off",
    )


def estimate_table3_from_figure5a_volumes(**inputs: Any) -> Table3ReproductionResult:
    """Estimate the bounded Table 3 pathway from Figure 5a and inferred R_b."""
    resolved = _resolve_inputs(inputs)
    published_table3 = _copy_frame(resolved["published_table3"])
    calculated_table3 = _calculate_table3_dataframe(resolved)
    comparison = _build_comparison_dataframe(published_table3, calculated_table3)
    validation = _validate_table3(
        resolved=resolved,
        published_table3=published_table3,
        calculated_table3=calculated_table3,
        comparison=comparison,
    )

    return Table3ReproductionResult(
        dataframe=_copy_frame(comparison),
        published_dataframe=_copy_frame(published_table3),
        calculated_dataframe=_copy_frame(calculated_table3),
        comparison_dataframe=_copy_frame(comparison),
        validation_summary={
            "published_fixture_integrity_passed": (
                validation.published_fixture_integrity_passed
            ),
            "calculated_pathway_passed": validation.calculated_pathway_passed,
            "passed": validation.passed,
        },
        known_residual_mismatches=validation.expected_residual_mismatches,
        clipped_cells=validation.clipped_cells,
        units={
            "edr_threshold_w_m3": ENERGY_DISSIPATION_RATE_W_M3,
            "affected_volume_nl": "nL",
            "bubble_volume_m3": VOLUME_M3,
            "event_count": EVENT_COUNT,
            "calc_viability_fraction": VIABILITY_FRACTION,
            "calc_viability_pct_rounded": VIABILITY_PERCENT,
            "clipped": "boolean",
        },
        inputs={
            "edr_thresholds_w_m3": list(resolved["edr_thresholds_w_m3"]),
            "total_gas_volume_l": resolved["total_gas_volume_l"],
            "system_volume_l": resolved["system_volume_l"],
            "initial_viability_pct": resolved["initial_viability_pct"],
            "single_event_viability_loss_pct": (
                resolved["single_event_viability_loss_pct"]
            ),
        },
        input_provenance={
            field: resolved["_pathway_input_provenance"][field]
            for field in _PATHWAY_INPUT_PROVENANCE_FIELDS
        },
        source=MCRAE_2024_TABLE_3,
        assumptions=deepcopy(resolved["assumptions"]),
        notes=[
            (
                "Reconstructs the McRae 2024 Table 3 pathway from Figure 5a-derived "
                "affected volumes and inferred calculator R_b values, with two "
                "documented residual mismatch cells."
            )
        ],
        warnings=validation.warnings.copy(),
        model_context=MCRAE_2024_TABLE3_CONTEXT,
        event_context="pinch_off",
    )


def reproduce_table3(**inputs: Any) -> Table3ReproductionResult:
    """Reconstruct the bounded McRae 2024 Table 3 pathway with validation metadata."""
    return estimate_table3_from_figure5a_volumes(**inputs)


def validate_table3_against_published(**inputs: Any) -> Table3ValidationResult:
    """Validate published fixture exactness and expected pathway residual mismatches."""
    resolved = _resolve_inputs(inputs)
    published_table3 = _copy_frame(resolved["published_table3"])
    calculated_table3 = _calculate_table3_dataframe(resolved)
    comparison = _build_comparison_dataframe(published_table3, calculated_table3)
    return _validate_table3(
        resolved=resolved,
        published_table3=published_table3,
        calculated_table3=calculated_table3,
        comparison=comparison,
    )
