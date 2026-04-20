# Model Boundaries

The first-class v0.1 packaged viability model is McRae et al. 2024 pinch-off / Table 3 only.

`thalmetis-edr` v0.1 is a scaffold for published affected-volume and pinch-off
viability calculations. It is for research and educational reproducibility and
sensitivity analysis.

Walls et al. 2017 affected-volume-only support is limited to framing and, in a
future release, possible affected-volume-only helpers if they can be
implemented directly from published equations, data, or figures.

v0.1 has no rupture viability model. v0.1 has no combined pinch-off + rupture
viability model. Generic Equation 3 use outside McRae 2024 pinch-off is a
user-composed exploratory calculation, not a packaged validated model.

Public high-level calculation functions are designed to return structured
result objects with computed values, units, inputs, input provenance, source
equations or tables, assumptions, notes, and warnings.

v0.1 does not include a GUI, web app, dashboard, API server, cloud workflow, or
customer workflow. Any future GUI should live in a separate repository such as
`thalmetis-edr-ui` and depend on this core package.

## Explicit Exclusions

- no rupture viability model
- no combined pinch-off + rupture viability model
- no coalescence model
- no path-independence model
- no event-history viability implementation
- no thesis Table 4.4 implementation
- no CFD solver
- no ML or XGBoost model
- no GMP or process-control claim
- no commercial product workflow
