# Pinch-Off Viability Estimate

`estimate_pinchoff_viability(...)` is a bounded sensitivity estimate for the
McRae 2024 pinch-off pathway. It is not a validated industrial viability
prediction.

Affected volume comes from the packaged McRae 2024 Figure 5a interpolation
pathway. Bubble radius comes from caller input or, when explicitly allowed by
default fallback behavior, from the inferred Table 3 calculator `R_b`
interpolation. User-supplied bubble radius is preferred when available.

The inferred Table 3 `R_b` values are not measured bubble-size data. They are
calculator radii from the v0.1 Table 3 reconciliation.

Gas exposure can be supplied in one of three mutually exclusive modes:

- direct cumulative gas volume
- gas flow plus exposure duration
- VVM plus exposure duration

VVM mode treats system volume as constant over the exposure duration. The API
does not model fed-batch volume changes, gas uptake, gas production, kLa, OTR,
or changing system volume.

The API does not infer cell-line thresholds. The user supplies the EDR
threshold and single-event viability-loss assumptions.

The API does not know media, growth phase, passage, Pluronic concentration,
repair dynamics, residence-time effects, gas uptake, gas production, kLa, OTR,
or proprietary cell-line resilience.

This is not process control, GMP release, process approval, transfer approval,
or batch release. No rupture, coalescence, path-history, or thesis Table 4.4
behavior is included.
