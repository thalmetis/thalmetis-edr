"""Minimal example for the bounded McRae et al. 2024 Table 3 pathway."""

from thalmetis_edr import reproduce_table3


def main() -> None:
    """Show the structured Table 3 pathway result shape."""
    result = reproduce_table3()
    print("Validation summary:")
    print(result.validation_summary)
    print("\nCalculated Table 3 pathway viability columns:")
    print(
        result.calculated_dataframe[
            [
                "thread_radius_um",
                "calc_viability_1e6_pct_rounded",
                "calc_viability_1e7_pct_rounded",
                "calc_viability_1e8_pct_rounded",
            ]
        ]
    )


if __name__ == "__main__":
    main()
