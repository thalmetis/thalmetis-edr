# Future Event History

`ExposureHistory` is metadata-only in v0.1. It exists so later releases can
represent event-history concepts without changing the public shape of result
objects.

Thesis-derived coalescence, rupture, and path-independence ideas may be future
v0.2+ experimental modules only after IP and paper review.

v0.1 does not implement:

- coalescence
- event-history viability
- path-independence
- rupture + pinch-off composition
- thesis Table 4.4

No v0.1 API estimates viability from an `ExposureHistory`, combines rupture and
pinch-off effects, or packages rupture viability behavior.
