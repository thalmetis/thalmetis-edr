"""Metadata-only exposure containers for future event-history work."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ThresholdExposure:
    """Metadata for a threshold-defined exposure region."""

    event_kind: str = "generic"
    source: str = ""
    assumptions: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EventContribution:
    """Metadata for one future event-history contribution."""

    event_kind: str = "generic"
    source: str = ""
    assumptions: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExposureHistory:
    """Metadata-only container reserved for future event-history work.

    Accepted event-kind metadata may include "pinch_off", "rupture",
    "coalescence", "generic", and "future_experimental". v0.1 does not
    implement combined exposure, event-history viability, coalescence,
    rupture-composition, path-independence, or thesis Table 4.4 logic.
    """

    contributions: list[EventContribution] = field(default_factory=list)
    source: str = ""
    assumptions: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def estimate_viability(self) -> None:
        """Explicitly unavailable future-looking event-history stub."""
        raise NotImplementedError(
            "Estimating viability from ExposureHistory is out of scope for v0.1."
        )
