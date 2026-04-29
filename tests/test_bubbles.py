import math
from typing import get_type_hints

import pytest

from thalmetis_edr.bubbles import bubble_volume, event_count_from_gas_volume
from thalmetis_edr.results import BubbleVolumeResult, EventCountResult
from thalmetis_edr.units import liters_to_m3, mm_to_m


def test_bubble_stubs_return_structured_annotations() -> None:
    assert get_type_hints(bubble_volume)["return"] is BubbleVolumeResult
    assert get_type_hints(event_count_from_gas_volume)["return"] is EventCountResult


def test_bubble_volume_uses_spherical_geometry() -> None:
    radius_m = mm_to_m(0.18)
    result = bubble_volume(bubble_radius_m=radius_m)

    assert result.bubble_volume_m3 == pytest.approx((4.0 / 3.0) * math.pi * radius_m**3)


def test_event_count_from_gas_volume_divides_total_gas_by_bubble_volume() -> None:
    bubble_result = bubble_volume(bubble_radius_m=mm_to_m(0.18))
    event_result = event_count_from_gas_volume(
        cumulative_gas_volume_m3=liters_to_m3(1_152_000.0),
        bubble_volume_m3=bubble_result.bubble_volume_m3,
    )

    assert event_result.event_count == pytest.approx(
        liters_to_m3(1_152_000.0) / bubble_result.bubble_volume_m3
    )
