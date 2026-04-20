"""Source labels and placeholders for McRae et al. 2024.

McRae et al. 2024 is the first-class v0.1 packaged viability source for
pinch-off / sparging affected volume, event count, Equation 3 viability, and
Table 3 reproduction. No computation is implemented in this scaffold PR.
"""

from __future__ import annotations

from typing import Any

MCRAE_2024_EQ_2 = "McRae et al. 2024 Eq. 2"
MCRAE_2024_EQ_3 = "McRae et al. 2024 Eq. 3"
MCRAE_2024_TABLE_3 = "McRae et al. 2024 Table 3"

MCRAE_2024_MODEL_CONTEXT = "mcrae_2024_pinch_off"
MCRAE_2024_TABLE3_CONTEXT = "mcrae_2024_table3"

TABLE3_INPUT_PLACEHOLDERS: dict[str, Any] = {
    "source": MCRAE_2024_TABLE_3,
    "model_context": MCRAE_2024_TABLE3_CONTEXT,
    "notes": [
        "Placeholder for published Table 3 inputs.",
        "No numerical values are implemented in the scaffold PR.",
    ],
}

TABLE3_ASSUMPTIONS_PLACEHOLDER: dict[str, Any] = {
    "source": MCRAE_2024_TABLE_3,
    "status": "scaffold_only",
}
