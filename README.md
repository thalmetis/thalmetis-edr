# thalmetis-edr

`thalmetis-edr` is a small open-source Python toolkit for bounded published
pathway reconstruction, interpolation, and sensitivity analysis around
energy-dissipation-rate (EDR) exposure from bubble pinch-off. It is intended
for research and educational use.

v0.1 reconstructed the bounded McRae 2024 Figure 5a/Table 3 pathway from
Figure 5a-derived affected volumes and inferred calculator `R_b` values, with
two documented residual mismatch cells.

v0.2 adds bounded interpolation and user-defined pinch-off sensitivity
estimates within the packaged Figure 5a / Table 3 domains:

- `interpolate_pinchoff_affected_volume(...)`
- `interpolate_table3_bubble_radius(...)`
- `estimate_pinchoff_viability(...)`

`estimate_pinchoff_viability(...)` is a bounded sensitivity estimate. It is not
a validated industrial viability predictor.

## Installation

PyPI publication is intentionally deferred. Install from source:

```powershell
git clone https://github.com/thalmetis/thalmetis-edr.git
cd thalmetis-edr
python -m pip install -e .
```

For development:

```powershell
python -m pip install -e ".[dev]"
```

## Table 3 Quickstart

Reconstruct and validate the bounded McRae 2024 Figure 5a / Table 3 pathway:

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

The Table 3 pathway uses Figure 5a-derived affected volumes and inferred
calculator `R_b` values. It reports two documented residual mismatch cells
rather than claiming exact independent Table 3 reproduction:

- `100 um / 1e8 W/m^3`: calculated `96%`, published `97%`
- `1250 um / 1e6 W/m^3`: calculated `99%`, published `100%`

## v0.2 Quickstart

Interpolate packaged Figure 5a affected volume:

```python
from thalmetis_edr import interpolate_pinchoff_affected_volume

affected = interpolate_pinchoff_affected_volume(
    thread_radius_um=75.0,
    edr_threshold_w_m3=5.0e6,
)

print(affected.affected_volume_nl)
print(affected.metadata.bracketing_thread_radius_um)
```

Optionally interpolate inferred Table 3 calculator `R_b` values. These are not
measured bubble-size data and are not a general sparger bubble-size model:

```python
from thalmetis_edr import interpolate_table3_bubble_radius

inferred_radius = interpolate_table3_bubble_radius(thread_radius_um=75.0)

print(inferred_radius.bubble_radius_mm)
print(inferred_radius.warnings)
```

Estimate bounded pinch-off viability sensitivity. Prefer user-supplied bubble
radius when available:

```python
from thalmetis_edr import estimate_pinchoff_viability

estimate = estimate_pinchoff_viability(
    thread_radius_um=75.0,
    edr_threshold_w_m3=5.0e6,
    system_volume_l=10.0,
    initial_viability_pct=95.0,
    single_event_viability_loss_pct=10.0,
    gas_flow_rate_l_min=0.2,
    exposure_duration_h=4.0,
    bubble_radius_mm=0.8,
)

print(estimate.raw_final_viability_pct)
print(estimate.final_viability_pct)
print(estimate.bubble_radius_source)
print(estimate.warnings)
```

Gas exposure can be supplied as:

- direct cumulative gas volume: `total_gas_volume_l`
- gas flow plus duration: `gas_flow_rate_l_min` and `exposure_duration_h`
- VVM plus duration: `vvm` and `exposure_duration_h`

Users supply the EDR threshold and single-event viability-loss assumptions. The
package does not infer cell-line thresholds.

## Structured Results

Public high-level calculation functions return structured result objects
instead of bare floats. These objects carry:

- computed values
- units
- original input values
- input provenance
- source equation or source table
- assumptions
- notes or warnings

This structured-return design supports notebooks, wrappers, and possible future
interfaces while keeping the scientific assumptions visible.

## Boundaries

Within the broader Thalmetis project, this repository is the open scientific
methodology track: hydrodynamic research tooling for reproducibility and
sensitivity analysis. It is not the main commercial Thalmetis
transfer-readiness product.

`thalmetis-edr` does not include:

- validated industrial viability prediction
- process control, GMP release, transfer approval, process approval, or batch
  release
- automatic cell-line threshold lookup
- extrapolation outside packaged interpolation domains
- McRae 2024 Equation 2 as an operational model
- rupture viability
- coalescence
- path-history or path-independence behavior
- thesis Table 4.4
- sparger optimization
- CFD/local-stress-field workflows
- GUI, web app, dashboard, API server, or cloud workflow

Walls et al. 2017 affected-volume-only context supports the affected-volume
framing and the critique of relying on a single maximum EDR. Future Walls et
al. 2017 helpers may be added only as affected-volume-only calculations if they
can be implemented directly from published equations, data, or figures.

## Citation

For v0.2.0, cite:

McRae, O. (2026). thalmetis-edr (v0.2.0). Zenodo.
https://doi.org/10.5281/zenodo.19961963

For the evolving package across all versions, use the concept DOI:
https://doi.org/10.5281/zenodo.19932773

The v0.1.0 archive DOI is
https://doi.org/10.5281/zenodo.19932774. This is a v0.1.0 archive note and is
not presented as the current v0.2.0 package citation.

Also cite the relevant scientific papers in `docs/references.md`.

## Development

Run the package checks:

```powershell
python -m pytest
python -m ruff check .
```
