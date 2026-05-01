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


@dataclass(frozen=True, slots=True)
class InterpolationMetadata:
    """Interpolation metadata for packaged affected-volume estimates."""

    method: str
    source_table: str
    input_thread_radius_um: float
    input_edr_threshold_w_m3: float
    bracketing_thread_radius_um: tuple[float, float]
    bracketing_edr_threshold_w_m3: tuple[float, float]
    exact_grid_point: bool
    interpolation_space: str
    domain_min_thread_radius_um: float
    domain_max_thread_radius_um: float
    domain_min_edr_threshold_w_m3: float
    domain_max_edr_threshold_w_m3: float
    extrapolated: bool
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PinchoffAffectedVolumeEstimate:
    """Interpolated McRae Figure 5a pinch-off affected-volume estimate."""

    affected_volume_nl: float
    affected_volume_m3: float
    thread_radius_um: float
    edr_threshold_w_m3: float
    metadata: InterpolationMetadata
    assumptions: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Table3BubbleRadiusInterpolationMetadata:
    """Interpolation metadata for inferred Table 3 calculator bubble radii."""

    method: str
    source_table: str
    source_column: str
    input_thread_radius_um: float
    bracketing_thread_radius_um: tuple[float, float]
    exact_grid_point: bool
    interpolation_space: str
    domain_min_thread_radius_um: float
    domain_max_thread_radius_um: float
    extrapolated: bool
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Table3BubbleRadiusEstimate:
    """Interpolated inferred Table 3 calculator bubble-radius estimate."""

    bubble_radius_mm: float
    bubble_radius_m: float
    thread_radius_um: float
    metadata: Table3BubbleRadiusInterpolationMetadata
    assumptions: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PinchoffViabilityEstimate:
    """Bounded McRae 2024 pinch-off viability sensitivity estimate."""

    final_viability_pct: float
    raw_final_viability_pct: float
    clipped: bool

    initial_viability_pct: float
    single_event_viability_loss_pct: float

    thread_radius_um: float
    edr_threshold_w_m3: float

    affected_volume_nl: float
    affected_volume_m3: float

    bubble_radius_mm: float
    bubble_radius_m: float
    bubble_radius_source: str

    bubble_volume_m3: float

    gas_exposure_mode: str
    total_gas_volume_l: float
    total_gas_volume_m3: float
    gas_flow_rate_l_min: float | None
    exposure_duration_h: float | None
    vvm: float | None

    system_volume_l: float
    system_volume_m3: float
    event_count: float

    affected_volume_metadata: InterpolationMetadata
    bubble_radius_metadata: Table3BubbleRadiusInterpolationMetadata | None

    assumptions: tuple[str, ...]
    warnings: tuple[str, ...]
    source_provenance: tuple[str, ...]


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
    clipped_cells: list[Metadata] = field(default_factory=list)
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
    missing_published_keys: list[Metadata] = field(default_factory=list)
    extra_published_keys: list[Metadata] = field(default_factory=list)
    duplicate_published_keys: list[Metadata] = field(default_factory=list)
    missing_calculated_keys: list[Metadata] = field(default_factory=list)
    extra_calculated_keys: list[Metadata] = field(default_factory=list)
    duplicate_calculated_keys: list[Metadata] = field(default_factory=list)
    clipped_cells: list[Metadata] = field(default_factory=list)
    units: StringMap = field(default_factory=dict)
    inputs: Metadata = field(default_factory=dict)
    input_provenance: StringMap = field(default_factory=dict)
    source: str = "McRae et al. 2024 Table 3"
    assumptions: Metadata = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    model_context: str = "mcrae_2024_table3"
    event_context: str = "pinch_off"
