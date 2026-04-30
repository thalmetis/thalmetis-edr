"""Public API for the bounded thalmetis-edr v0.1 package."""

from thalmetis_edr.affected_volume import (
    affected_volume_from_threshold,
    walls_2017_rupture_affected_volume,
)
from thalmetis_edr.bubbles import bubble_volume, event_count_from_gas_volume
from thalmetis_edr.exposure import EventContribution, ExposureHistory, ThresholdExposure
from thalmetis_edr.results import (
    AffectedVolumeResult,
    BubbleVolumeResult,
    EventCountResult,
    Table3ReproductionResult,
    Table3ValidationResult,
    ViabilityEstimate,
    ViabilitySensitivityResult,
)
from thalmetis_edr.tables import (
    estimate_table3_from_figure5a_volumes,
    mcrae_2024_figure5a_volumes,
    mcrae_2024_published_table3,
    mcrae_2024_table3_inputs,
    reproduce_table3,
    validate_table3_against_published,
)
from thalmetis_edr.viability import (
    estimate_viability_after_events,
    viability_sensitivity,
)

__all__ = [
    "AffectedVolumeResult",
    "BubbleVolumeResult",
    "EventContribution",
    "EventCountResult",
    "ExposureHistory",
    "Table3ReproductionResult",
    "Table3ValidationResult",
    "ThresholdExposure",
    "ViabilityEstimate",
    "ViabilitySensitivityResult",
    "affected_volume_from_threshold",
    "bubble_volume",
    "estimate_table3_from_figure5a_volumes",
    "estimate_viability_after_events",
    "event_count_from_gas_volume",
    "mcrae_2024_figure5a_volumes",
    "mcrae_2024_published_table3",
    "mcrae_2024_table3_inputs",
    "reproduce_table3",
    "validate_table3_against_published",
    "viability_sensitivity",
    "walls_2017_rupture_affected_volume",
]
