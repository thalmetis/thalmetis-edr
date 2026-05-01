# Model Boundaries

`thalmetis-edr` is Track B open scientific hydrodynamic methodology tooling for
research and educational use. It is not the main commercial Thalmetis
transfer-readiness product.

v0.1 implemented the fixed bounded McRae 2024 Figure 5a / Table 3
reconstruction from Figure 5a-derived affected volumes and inferred calculator
`R_b` values.

v0.2 adds bounded interpolation and pinch-off sensitivity estimation within the
packaged Figure 5a / Table 3 domains:

- Figure 5a interpolation is affected-volume interpolation only.
- Table 3 `R_b` interpolation uses inferred calculator radii from the v0.1
  reconciliation, not measured bubble-size data.
- Pinch-off viability is a bounded sensitivity estimate only.

Users supply EDR threshold and single-event viability-loss assumptions. The
package does not infer cell-line thresholds.

McRae 2024 Equation 2 remains a published analytical scaling reference. It is
not implemented as an operational model in this package.

Public high-level calculation functions are designed to return structured
result objects with computed values, units, inputs, input provenance, source
equations or tables, assumptions, notes, and warnings.

## Explicit Exclusions

- no validated industrial viability prediction
- no process control, GMP release, transfer approval, process approval, or
  batch release
- no Track A transfer-readiness integration
- no Equation 2 operational model
- no extrapolation outside packaged interpolation domains
- no automatic cell-line threshold lookup
- no rupture viability model
- no combined pinch-off + rupture viability model
- no coalescence model
- no path-independence or path-history model
- no event-history viability implementation
- no thesis Table 4.4 implementation
- no CFD solver or local-stress-field workflow
- no sparger optimizer
- no ML or XGBoost model
- no GUI, web app, dashboard, API server, cloud workflow, or customer workflow
