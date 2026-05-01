# Table 3 Bubble-Radius Interpolation

`interpolate_table3_bubble_radius(...)` is a bounded interpolation primitive for
the packaged inferred calculator `R_b` values from the v0.1 McRae 2024 Table 3
reconciliation.

These values are not raw measured bubble-radius data. This function is not a
general physical sparger bubble-size model.

## Domain

The supported domain is the packaged thread-radius fixture domain, expected to
be `10` to `1250 um`.

The input is `thread_radius_um`, meaning thread radius. If a vendor provides a
pore diameter, divide by two before using this API.

Inputs outside the packaged domain raise `ValueError`. No extrapolation is
performed.

## Interpolation

The supported method is `loglog_linear`.

The interpolation coordinates are:

- `x = log10(thread_radius_um)`
- `z = log10(bubble_radius_mm)`

Exact grid-point requests return the packaged inferred calculator `R_b` value
directly. Interior points use log-log linear interpolation between the
bracketing packaged thread radii.

## Boundaries

This PR does not estimate viability.

In later viability workflows, affected volume should be based on thread radius
and EDR threshold. Event count should be based on user-supplied bubble radius
or, if absent and explicitly allowed, this inferred Table 3 `R_b`
interpolation. User-supplied bubble radius should be preferred when available.

This primitive does not introduce a process-control, GMP, process-approval,
hosted/web/server/cloud API, or validated industrial prediction claim.
