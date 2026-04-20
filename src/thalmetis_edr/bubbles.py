"""Bubble-volume and event-count stubs for McRae 2024 Table 3 support."""

from __future__ import annotations

from typing import Any

from thalmetis_edr.published.mcrae_2024 import MCRAE_2024_TABLE_3
from thalmetis_edr.results import BubbleVolumeResult, EventCountResult


def bubble_volume(
    *,
    bubble_diameter_m: float | None = None,
    **inputs: Any,
) -> BubbleVolumeResult:
    """Scaffold bubble-volume calculation for McRae 2024 pinch-off events."""
    raise NotImplementedError(
        "Bubble-volume equations are not implemented in the v0.1 scaffold PR."
    )


def event_count_from_gas_volume(
    *,
    cumulative_gas_volume_m3: float | None = None,
    bubble_volume_m3: float | None = None,
    source: str = MCRAE_2024_TABLE_3,
    **inputs: Any,
) -> EventCountResult:
    """Scaffold event count from cumulative gas volume and bubble volume."""
    raise NotImplementedError(
        "Event-count equations are not implemented in the v0.1 scaffold PR."
    )
