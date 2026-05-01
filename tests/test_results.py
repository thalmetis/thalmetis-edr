from thalmetis_edr.results import (
    AffectedVolumeResult,
    BubbleVolumeResult,
    EventCountResult,
    InterpolationMetadata,
    PinchoffAffectedVolumeEstimate,
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
    metadata = InterpolationMetadata(
        method="loglog_bilinear",
        source_table="test",
        input_thread_radius_um=100.0,
        input_edr_threshold_w_m3=1.0e7,
        bracketing_thread_radius_um=(100.0, 100.0),
        bracketing_edr_threshold_w_m3=(1.0e7, 1.0e7),
        exact_grid_point=True,
        interpolation_space="test",
        domain_min_thread_radius_um=10.0,
        domain_max_thread_radius_um=1250.0,
        domain_min_edr_threshold_w_m3=1.0e6,
        domain_max_edr_threshold_w_m3=1.0e8,
        extrapolated=False,
        warnings=(),
    )
    assert hasattr(metadata, "source_table")
    assert hasattr(
        PinchoffAffectedVolumeEstimate(
            affected_volume_nl=1.0,
            affected_volume_m3=1.0e-12,
            thread_radius_um=100.0,
            edr_threshold_w_m3=1.0e7,
            metadata=metadata,
            assumptions=(),
            warnings=(),
        ),
        "affected_volume_nl",
    )
    assert hasattr(ViabilityEstimate(), "final_viability")
    assert hasattr(ViabilitySensitivityResult(), "dataframe")
    assert hasattr(Table3ReproductionResult(), "dataframe")
    assert hasattr(Table3ReproductionResult(), "calculated_dataframe")
    assert hasattr(Table3ReproductionResult(), "clipped_cells")
    assert hasattr(Table3ValidationResult(), "passed")
    assert hasattr(Table3ValidationResult(), "expected_residual_mismatches")
    assert hasattr(Table3ValidationResult(), "clipped_cells")
