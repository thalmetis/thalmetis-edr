"""Minimal bounded pinch-off viability sensitivity example."""

from thalmetis_edr import estimate_pinchoff_viability


def _print_estimate(label: str, estimate: object) -> None:
    print(f"\n{label}")
    print(f"raw viability: {estimate.raw_final_viability_pct:.6f}%")
    print(f"clipped viability: {estimate.final_viability_pct:.6f}%")
    print(f"clipped: {estimate.clipped}")
    print(f"bubble-radius source: {estimate.bubble_radius_source}")
    print("selected warnings:")
    for warning in estimate.warnings[:3]:
        print(f"- {warning}")
    print("selected provenance:")
    for source in estimate.source_provenance:
        print(f"- {source}")


def main() -> None:
    """Show user-supplied and inferred-radius sensitivity estimate paths."""
    print("bounded sensitivity estimate")
    print("not a validated prediction")
    print("user-supplied bubble radius preferred")
    print("inferred Table 3 R_b fallback is not measured bubble-size data")

    user_radius = estimate_pinchoff_viability(
        thread_radius_um=75.0,
        edr_threshold_w_m3=5.0e6,
        system_volume_l=10.0,
        initial_viability_pct=95.0,
        single_event_viability_loss_pct=10.0,
        gas_flow_rate_l_min=0.2,
        exposure_duration_h=4.0,
        bubble_radius_mm=0.8,
    )
    inferred_radius = estimate_pinchoff_viability(
        thread_radius_um=75.0,
        edr_threshold_w_m3=5.0e6,
        system_volume_l=10.0,
        initial_viability_pct=95.0,
        single_event_viability_loss_pct=10.0,
        gas_flow_rate_l_min=0.2,
        exposure_duration_h=4.0,
        bubble_radius_mm=None,
        use_inferred_bubble_radius=True,
    )

    _print_estimate("User-supplied bubble radius path", user_radius)
    _print_estimate("Optional inferred Table 3 R_b fallback path", inferred_radius)


if __name__ == "__main__":
    main()
