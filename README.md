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

## Quickstart

Install the package in an environment of your choice:

```powershell
python -m pip install thalmetis-edr
```

Then reconstruct and validate the bounded McRae 2024 Figure 5a / Table 3
pathway:

```python
from thalmetis_edr import (
    mcrae_2024_published_table3,
    reproduce_table3,
    validate_table3_against_published,
)

published = mcrae_2024_published_table3()
result = reproduce_table3()
validation = validate_table3_against_published()

print(result.validation_summary)
print(result.known_residual_mismatches)
print(validation.expected_residual_mismatches)
print(published.head())
```

Expected validation summary:

```python
{
    "published_fixture_integrity_passed": True,
    "calculated_pathway_passed": True,
    "passed": True,
}
```

The v0.1 pathway uses Figure 5a-derived affected volumes and inferred
calculator `R_b` values. It reports two documented residual mismatch cells
rather than claiming exact independent Table 3 reproduction:

- `100 um / 1e8 W/m^3`: calculated `96%`, published `97%`
- `1250 um / 1e6 W/m^3`: calculated `99%`, published `100%`

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

McRae 2024 Equation 2 remains a published analytical scaling reference in
v0.1. It is intentionally not implemented as the operational Table 3 pathway.

## Interfaces

v0.1 does not include a GUI, web app, dashboard, API server, cloud workflow, or
customer workflow. Any future GUI should live in a separate repository such as
`thalmetis-edr-ui` and depend on this core package.

## What This Is Not

- not CFD
- not a validated industrial viability predictor
- not a universal viability predictor
- not a GMP decision tool
- not a process decision tool
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
