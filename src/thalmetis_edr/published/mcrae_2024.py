"""Published-source metadata for McRae et al. 2024.

McRae et al. 2024 is the first-class v0.1 packaged viability source for the
bounded pinch-off / sparging Figure 5a and Table 3 pathway.
"""

from __future__ import annotations

from typing import Any

MCRAE_2024_EQ_2 = "McRae et al. 2024 Eq. 2"
MCRAE_2024_EQ_3 = "McRae et al. 2024 Eq. 3"
MCRAE_2024_TABLE_3 = "McRae et al. 2024 Table 3"
MCRAE_2024_FIGURE_5A = "McRae et al. 2024 Figure 5a"

MCRAE_2024_MODEL_CONTEXT = "mcrae_2024_pinch_off"
MCRAE_2024_TABLE3_CONTEXT = "mcrae_2024_table3"

MCRAE_2024_FIGURE5A_VOLUME_FILENAME = "mcrae_2024_figure5a_bub80compare9_volumes.csv"
MCRAE_2024_TABLE3_PUBLISHED_FILENAME = "mcrae_2024_table3_published.csv"
MCRAE_2024_TABLE3_INFERRED_RADII_FILENAME = "mcrae_2024_table3_inferred_radii.csv"

MCRAE_2024_FIGURE5A_SOURCE = (
    "bub80compare9.m near-final author-script inferred Figure 5a affected-volume data"
)
MCRAE_2024_TABLE3_PUBLISHED_SOURCE = "McRae et al. 2024 Table 3 published fixture"
MCRAE_2024_TABLE3_INFERRED_RADII_SOURCE = (
    "inferred calculator R_b values consistent with rounded Table 3 display "
    "and the bub80compare9.m volume arrays"
)
MCRAE_2024_TABLE3_BUBBLE_VOLUME_SOURCE = (
    "Spherical bubble volume from inferred calculator R_b values"
)
MCRAE_2024_TABLE3_EVENT_COUNT_SOURCE = (
    "Event count from cumulative gas volume divided by spherical bubble volume"
)

MCRAE_2024_TABLE3_THRESHOLDS_W_M3: tuple[float, float, float] = (
    1.0e6,
    1.0e7,
    1.0e8,
)
MCRAE_2024_TABLE3_TOTAL_GAS_VOLUME_L = 1_152_000.0
MCRAE_2024_TABLE3_SYSTEM_VOLUME_L = 5000.0
MCRAE_2024_TABLE3_INITIAL_VIABILITY_PCT = 100.0
MCRAE_2024_TABLE3_SINGLE_EVENT_VIABILITY_LOSS_PCT = 100.0

MCRAE_2024_TABLE3_KNOWN_RESIDUAL_MISMATCHES: tuple[dict[str, Any], ...] = (
    {
        "thread_radius_um": 100,
        "edr_threshold_w_m3": 1.0e8,
        "calculated_viability_pct_rounded": 96,
        "published_viability_pct": 97,
    },
    {
        "thread_radius_um": 1250,
        "edr_threshold_w_m3": 1.0e6,
        "calculated_viability_pct_rounded": 99,
        "published_viability_pct": 100,
    },
)

MCRAE_2024_TABLE3_PATHWAY_METADATA: dict[str, Any] = {
    "source": MCRAE_2024_TABLE_3,
    "model_context": MCRAE_2024_TABLE3_CONTEXT,
    "edr_thresholds_w_m3": list(MCRAE_2024_TABLE3_THRESHOLDS_W_M3),
    "total_gas_volume_l": MCRAE_2024_TABLE3_TOTAL_GAS_VOLUME_L,
    "system_volume_l": MCRAE_2024_TABLE3_SYSTEM_VOLUME_L,
    "initial_viability_pct": MCRAE_2024_TABLE3_INITIAL_VIABILITY_PCT,
    "single_event_viability_loss_pct": (
        MCRAE_2024_TABLE3_SINGLE_EVENT_VIABILITY_LOSS_PCT
    ),
    "sources": {
        "figure5a_volumes": MCRAE_2024_FIGURE5A_SOURCE,
        "published_table3": MCRAE_2024_TABLE3_PUBLISHED_SOURCE,
        "inferred_radii": MCRAE_2024_TABLE3_INFERRED_RADII_SOURCE,
    },
    "notes": [
        (
            "Reconstructs the McRae 2024 Table 3 pathway from Figure 5a-derived "
            "affected volumes and inferred calculator R_b values, with two "
            "documented residual mismatch cells."
        ),
        (
            "Equation 2 is a published analytical scaling reference and is "
            "intentionally not the operational Table 3 pathway in v0.1."
        ),
        (
            "Figure 5a affected volumes use V/Vt normalization with "
            "Vt = 10 * pi * R_t^3 and V = (V/Vt) * 10 * pi * R_t^3."
        ),
    ],
    "assumptions": {
        "bubble_volume_model": "spherical bubble volume from inferred R_b",
        "event_count_model": "cumulative gas volume / bubble volume",
        "equation_3_model": "Psi = Psi0 - DeltaPsi_n * Nevents * Vaffected / Vsystem",
        "equation_2_status": "deferred_not_used_for_table3_pathway",
    },
}
