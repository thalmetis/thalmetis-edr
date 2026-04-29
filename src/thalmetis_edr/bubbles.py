"""Bubble-volume and event-count helpers for McRae 2024 Table 3 support."""

from __future__ import annotations

import math
from typing import Any

from thalmetis_edr.published.mcrae_2024 import (
    MCRAE_2024_MODEL_CONTEXT,
    MCRAE_2024_TABLE3_BUBBLE_VOLUME_SOURCE,
    MCRAE_2024_TABLE3_EVENT_COUNT_SOURCE,
)
from thalmetis_edr.results import BubbleVolumeResult, EventCountResult
from thalmetis_edr.units import EVENT_COUNT, LENGTH_M, VOLUME_M3


def bubble_volume(
    *,
    bubble_radius_m: float | None = None,
    bubble_diameter_m: float | None = None,
    source: str = MCRAE_2024_TABLE3_BUBBLE_VOLUME_SOURCE,
    **inputs: Any,
) -> BubbleVolumeResult:
    """Calculate spherical bubble volume for McRae 2024 pinch-off events."""
    if bubble_radius_m is None and bubble_diameter_m is None:
        raise ValueError("Provide bubble_radius_m or bubble_diameter_m.")
    if bubble_radius_m is not None and bubble_diameter_m is not None:
        raise ValueError("Provide only one of bubble_radius_m or bubble_diameter_m.")

    radius_m = bubble_radius_m
    if radius_m is None:
        radius_m = bubble_diameter_m / 2.0

    if radius_m is None or radius_m <= 0.0:
        raise ValueError("Bubble radius must be positive.")

    bubble_volume_m3 = (4.0 / 3.0) * math.pi * (radius_m**3)
    return BubbleVolumeResult(
        bubble_volume_m3=bubble_volume_m3,
        units={"bubble_volume_m3": VOLUME_M3, "bubble_radius_m": LENGTH_M},
        inputs={"bubble_radius_m": radius_m, **inputs},
        input_provenance={"bubble_radius_m": "caller"},
        source=source,
        assumptions={"geometry": "sphere"},
        notes=["Uses spherical bubble volume from inferred or caller-supplied radius."],
        model_context=MCRAE_2024_MODEL_CONTEXT,
        event_context="pinch_off",
    )


def event_count_from_gas_volume(
    *,
    cumulative_gas_volume_m3: float | None = None,
    bubble_volume_m3: float | None = None,
    source: str = MCRAE_2024_TABLE3_EVENT_COUNT_SOURCE,
    **inputs: Any,
) -> EventCountResult:
    """Calculate event count from cumulative gas volume and bubble volume."""
    if cumulative_gas_volume_m3 is None or bubble_volume_m3 is None:
        raise ValueError(
            "Provide cumulative_gas_volume_m3 and bubble_volume_m3 for event count."
        )
    if cumulative_gas_volume_m3 < 0.0 or bubble_volume_m3 <= 0.0:
        raise ValueError("Gas volume must be non-negative and bubble volume positive.")

    event_count = cumulative_gas_volume_m3 / bubble_volume_m3
    return EventCountResult(
        event_count=event_count,
        units={
            "cumulative_gas_volume_m3": VOLUME_M3,
            "bubble_volume_m3": VOLUME_M3,
            "event_count": EVENT_COUNT,
        },
        inputs={
            "cumulative_gas_volume_m3": cumulative_gas_volume_m3,
            "bubble_volume_m3": bubble_volume_m3,
            **inputs,
        },
        input_provenance={
            "cumulative_gas_volume_m3": "caller",
            "bubble_volume_m3": "caller",
        },
        source=source,
        assumptions={"model": "cumulative gas volume / bubble volume"},
        notes=["Implements the Table 3 event-count pathway from total gas volume."],
        model_context=MCRAE_2024_MODEL_CONTEXT,
        event_context="pinch_off",
    )
