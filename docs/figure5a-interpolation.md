# Figure 5a Affected-Volume Interpolation

`interpolate_pinchoff_affected_volume(...)` is a bounded affected-volume
interpolation primitive for McRae et al. 2024 Figure 5a pathway data. It
returns affected volume only; it does not calculate viability.

## Scope

The packaged grid is McRae 2024 Figure 5a pathway data inferred during the
v0.1 reconciliation using a near-final author script. It is not described as
raw original simulation output.

The supported packaged interpolation domain is:

- thread radius: `10` to `1250 um`
- EDR threshold: `1e6` to `1e8 W/m^3`

Inputs outside that domain raise `ValueError`. No extrapolation is performed.

## Interpolation

The supported method is `loglog_bilinear`.

The interpolation coordinates are:

- `x = log10(thread_radius_um)`
- `y = log10(edr_threshold_w_m3)`
- `z = log10(affected_volume_nl)`

Exact grid-point requests return the packaged grid value directly. If only one
axis is an exact grid value, the calculation reduces internally to log-linear
interpolation on the other axis while retaining `method="loglog_bilinear"` in
the returned metadata.

## Boundaries

This primitive is intended for reproducibility and sensitivity analysis around
the packaged Figure 5a pathway data. It is not a validated industrial viability
predictor, not process-control software, and not a GMP decision tool.

This PR does not add:

- McRae 2024 Equation 2
- viability estimation
- bubble-radius interpolation
- rupture viability
- coalescence
- path-independence
- thesis Table 4.4
- unpublished 2026 hemolysis work
- ML or XGBoost
- GUI
- web/server/cloud or hosted API

The PR does add a public Python API for this affected-volume interpolation
primitive.
