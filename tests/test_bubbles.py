from typing import get_type_hints

import pytest

from thalmetis_edr.bubbles import bubble_volume, event_count_from_gas_volume
from thalmetis_edr.results import BubbleVolumeResult, EventCountResult


def test_bubble_stubs_return_structured_annotations() -> None:
    assert get_type_hints(bubble_volume)["return"] is BubbleVolumeResult
    assert get_type_hints(event_count_from_gas_volume)["return"] is EventCountResult


def test_bubble_stubs_are_scaffold_only() -> None:
    with pytest.raises(NotImplementedError):
        bubble_volume()

    with pytest.raises(NotImplementedError):
        event_count_from_gas_volume()
