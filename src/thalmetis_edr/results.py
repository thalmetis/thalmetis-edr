"""Structured result objects for public thalmetis-edr calculations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

Metadata = dict[str, Any]
StringMap = dict[str, str]


@dataclass(slots=True)
class AffectedVolumeResult:
    """Affected-volume result with source and provenance metadata."""

    affected_volume_m3: float | None = None
    units: StringMap = field(default_factory=dict)
    inputs: Metadata = field(default_factory=dict)
    input_provenance: StringMap = field(default_factory=dict)
    source: str = ""
    assumptions: Metadata = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    model_context: str = ""
    event_context: str = ""


@dataclass(slots=True)
class BubbleVolumeResult:
    """Bubble-volume result with source and provenance metadata."""

    bubble_volume_m3: float | None = None
    units: StringMap = field(default_factory=dict)
    inputs: Metadata = field(default_factory=dict)
    input_provenance: StringMap = field(default_factory=dict)
    source: str = ""
    assumptions: Metadata = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    model_context: str = ""
    event_context: str = "pinch_off"


@dataclass(slots=True)
class EventCountResult:
    """Event-count result with source and provenance metadata."""

    event_count: int | float | None = None
    units: StringMap = field(default_factory=dict)
    inputs: Metadata = field(default_factory=dict)
    input_provenance: StringMap = field(default_factory=dict)
    source: str = ""
    assumptions: Metadata = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    model_context: str = ""
    event_context: str = "pinch_off"


@dataclass(slots=True)
class ViabilityEstimate:
    """Viability estimate result with source and provenance metadata."""

    final_viability: float | None = None
    units: StringMap = field(default_factory=dict)
    inputs: Metadata = field(default_factory=dict)
    input_provenance: StringMap = field(default_factory=dict)
    source: str = ""
    assumptions: Metadata = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    model_context: str = "user_composed_exploratory"
    event_context: str = "generic"


@dataclass(slots=True)
class ViabilitySensitivityResult:
    """Sensitivity-analysis result with source and provenance metadata."""

    dataframe: Any | None = None
    units: StringMap = field(default_factory=dict)
    inputs: Metadata = field(default_factory=dict)
    input_provenance: StringMap = field(default_factory=dict)
    source: str = ""
    assumptions: Metadata = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    model_context: str = "user_composed_exploratory"
    event_context: str = "generic"


@dataclass(slots=True)
class Table3ReproductionResult:
    """McRae et al. 2024 Table 3 reproduction result."""

    dataframe: Any | None = None
    published_dataframe: Any | None = None
    calculated_dataframe: Any | None = None
    comparison_dataframe: Any | None = None
    validation_summary: Metadata = field(default_factory=dict)
    known_residual_mismatches: list[Metadata] = field(default_factory=list)
    units: StringMap = field(default_factory=dict)
    inputs: Metadata = field(default_factory=dict)
    input_provenance: StringMap = field(default_factory=dict)
    source: str = "McRae et al. 2024 Table 3"
    assumptions: Metadata = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    model_context: str = "mcrae_2024_table3"
    event_context: str = "pinch_off"


@dataclass(slots=True)
class Table3ValidationResult:
    """Validation result for comparing Table 3 reproduction to publication."""

    passed: bool = False
    dataframe: Any | None = None
    published_dataframe: Any | None = None
    calculated_dataframe: Any | None = None
    comparison_dataframe: Any | None = None
    published_fixture_integrity_passed: bool = False
    calculated_pathway_passed: bool = False
    expected_residual_mismatches: list[Metadata] = field(default_factory=list)
    unexpected_mismatches: list[Metadata] = field(default_factory=list)
    missing_expected_mismatches: list[Metadata] = field(default_factory=list)
    units: StringMap = field(default_factory=dict)
    inputs: Metadata = field(default_factory=dict)
    input_provenance: StringMap = field(default_factory=dict)
    source: str = "McRae et al. 2024 Table 3"
    assumptions: Metadata = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    model_context: str = "mcrae_2024_table3"
    event_context: str = "pinch_off"
