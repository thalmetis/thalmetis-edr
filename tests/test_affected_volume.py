from typing import get_type_hints

import pytest

from thalmetis_edr.affected_volume import (
    affected_volume_from_threshold,
    walls_2017_rupture_affected_volume,
)
from thalmetis_edr.results import AffectedVolumeResult


def test_affected_volume_stubs_return_structured_annotations() -> None:
    assert (
        get_type_hints(affected_volume_from_threshold)["return"]
        is AffectedVolumeResult
    )
    assert (
        get_type_hints(walls_2017_rupture_affected_volume)["return"]
        is AffectedVolumeResult
    )


def test_affected_volume_stubs_are_scaffold_only() -> None:
    with pytest.raises(NotImplementedError):
        affected_volume_from_threshold()

    with pytest.raises(NotImplementedError):
        walls_2017_rupture_affected_volume()
