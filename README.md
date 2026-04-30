# thalmetis-edr

`thalmetis-edr` is a small open-source Python toolkit for implementing
published affected-volume and pinch-off viability calculations. It is intended
for research and educational use as a reproducibility and sensitivity-analysis
tool.

The v0.1 package reconstructs the McRae et al. 2024 Table 3 pathway from
Figure 5a-derived affected volumes and inferred calculator `R_b` values, with
two documented residual mismatch cells.
The first-class v0.1 packaged viability model is McRae et al. 2024 pinch-off / Table 3 only.

Walls et al. 2017 affected-volume-only context supports the affected-volume
framing and the critique of relying on a single maximum EDR. Future Walls et
al. 2017 helpers may be added only as affected-volume-only calculations if they
can be implemented directly from published equations, data, or figures.

v0.1 has no rupture viability model and no combined pinch-off + rupture
viability model.

## Structured Results

Public high-level calculation functions are designed to return structured
result objects instead of bare floats. These objects carry:

- computed value
- units
- original input values
- input provenance
- source equation or source table
- assumptions
- notes or warnings

This structured-return design supports notebooks, wrappers, and possible future
interfaces while keeping the scientific assumptions visible.

## Generic Equation 3 Helper

`estimate_viability_after_events(...)` is a bounded McRae et al. 2024 Equation
3 helper that accepts user-supplied affected volume, event count, and
cell-response parameters. The first-class packaged v0.1 viability use is McRae
2024 pinch-off / Table 3 only.

Use outside the McRae 2024 pinch-off context is a user-composed exploratory
calculation. It is not a universal viability predictor.

## Interfaces

v0.1 does not include a GUI, web app, dashboard, API server, cloud workflow, or
customer workflow. Any future GUI should live in a separate repository such as
`thalmetis-edr-ui` and depend on this core package.

## What This Is Not

- not CFD
- not a validated industrial model
- not a universal viability predictor
- not a GMP decision tool
- not process-control software
- not a packaged rupture viability model
- not a packaged combined pinch-off + rupture viability model
- not a replacement for process development, MSAT, validation, or experimental
  confirmation
- not the main commercial Thalmetis transfer-readiness product

## Development

Install development dependencies in an environment of your choice:

```powershell
python -m pip install -e .[dev]
```

Run the package checks:

```powershell
python -m pytest
python -m ruff check .
```
