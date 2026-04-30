"""Affected-volume calculation stubs for published v0.1 sources."""

from __future__ import annotations

from typing import Any

from thalmetis_edr.published.mcrae_2024 import MCRAE_2024_EQ_2
from thalmetis_edr.published.walls_2017 import WALLS_2017_AFFECTED_VOLUME_CONTEXT
from thalmetis_edr.results import AffectedVolumeResult


def affected_volume_from_threshold(
    *,
    threshold_edr_w_m3: float | None = None,
    source: str = MCRAE_2024_EQ_2,
    **inputs: Any,
) -> AffectedVolumeResult:
    """Scaffold McRae 2024 pinch-off affected-volume calculation.

    The v0.1 package exposes the result shape and source metadata only. The
    published equation is intentionally not implemented in this PR.
    """
    raise NotImplementedError(
        "McRae et al. 2024 affected-volume equations are out of scope for the "
        "bounded v0.1 implementation."
    )


def walls_2017_rupture_affected_volume(
    *,
    threshold_edr_w_m3: float | None = None,
    source: str = WALLS_2017_AFFECTED_VOLUME_CONTEXT,
    **inputs: Any,
) -> AffectedVolumeResult:
    """Affected-volume-only placeholder for possible Walls 2017 support.

    This is not a rupture viability model. Future implementation is allowed
    only if it can be derived directly from published Walls et al. 2017
    equations, data, or figures, and it must return affected-volume-style
    results only.
    """
    raise NotImplementedError(
        "Walls et al. 2017 rupture affected-volume support is scaffold-only "
        "and does not implement rupture viability in v0.1."
    )
