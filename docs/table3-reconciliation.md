# Table 3 Reconciliation

`thalmetis-edr` v0.1 reconstructs the McRae et al. 2024 Table 3 pathway from
Figure 5a-derived affected volumes and inferred calculator `R_b` values, with
two documented residual mismatch cells.

## Operational Source Path

The operational affected-volume source for the packaged v0.1 Table 3 pathway is
the inferred Figure 5a affected-volume table derived from `bub80compare9.m`.
This package encodes that source as:

- `bub80compare9.m` near-final author-script inferred Figure 5a affected-volume data
- published Table 3 values exactly as displayed
- inferred calculator `R_b` values consistent with rounded Table 3 display and
  the `bub80compare9.m` volume arrays

These packaged inputs are not described as original raw simulation output.

## V/Vt Normalization

The Figure 5a pathway uses the script normalization `V/Vt`.

For the simulation setup used in this reconciliation:

- thread length was approximately `20 * R_t`
- two bubbles were created in the simulation
- per-bubble simulation thread volume is `Vt = 10 * pi * R_t^3`

The affected-volume conversion used for the packaged source table is therefore:

`V = (V/Vt) * 10 * pi * R_t^3`

This explains the apparent factor ambiguity around Figure 5b and supports using
the Figure 5a-derived affected-volume table, not Equation 2 alone, as the
operational Table 3 pathway basis.

## Equation 2 Boundary

Equation 2 remains a published analytical scaling reference in v0.1. It is
intentionally not the operational Table 3 pathway in this package.

`affected_volume_from_threshold(...)` remains deferred and continues to raise
`NotImplementedError` in this PR. No prefactor tuning, silent equation changes,
or hidden fitted constants are introduced.

## Residual Mismatch Cells

Using the packaged Figure 5a volumes, inferred calculator `R_b` values,
spherical bubble volume, cumulative gas volume divided by bubble volume, and
McRae Equation 3 arithmetic reproduces 8 of the 10 published Table 3 rows
exactly after rounding.

Two residual mismatch cells remain and are expected:

- `100 um / 1e8 W/m^3`: calculated `96%`, published `97%`
- `1250 um / 1e6 W/m^3`: calculated `99%`, published `100%`

The package reports these explicitly in validation output and does not tune them
away.
