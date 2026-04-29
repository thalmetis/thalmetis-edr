from thalmetis_edr.results import (
    AffectedVolumeResult,
    BubbleVolumeResult,
    EventCountResult,
    Table3ReproductionResult,
    Table3ValidationResult,
    ViabilityEstimate,
    ViabilitySensitivityResult,
)


def test_result_dataclasses_instantiate_with_minimal_metadata() -> None:
    results = [
        AffectedVolumeResult(source="test"),
        BubbleVolumeResult(source="test"),
        EventCountResult(source="test"),
        ViabilityEstimate(source="test"),
        ViabilitySensitivityResult(source="test"),
        Table3ReproductionResult(source="test"),
        Table3ValidationResult(source="test"),
    ]

    for result in results:
        assert result.units == {}
        assert result.inputs == {}
        assert result.input_provenance == {}
        assert result.assumptions == {}
        assert result.notes == []
        assert result.warnings == []


def test_named_payload_fields_exist() -> None:
    assert hasattr(AffectedVolumeResult(), "affected_volume_m3")
    assert hasattr(BubbleVolumeResult(), "bubble_volume_m3")
    assert hasattr(EventCountResult(), "event_count")
    assert hasattr(ViabilityEstimate(), "final_viability")
    assert hasattr(ViabilitySensitivityResult(), "dataframe")
    assert hasattr(Table3ReproductionResult(), "dataframe")
    assert hasattr(Table3ReproductionResult(), "calculated_dataframe")
    assert hasattr(Table3ReproductionResult(), "clipped_cells")
    assert hasattr(Table3ValidationResult(), "passed")
    assert hasattr(Table3ValidationResult(), "expected_residual_mismatches")
    assert hasattr(Table3ValidationResult(), "clipped_cells")
