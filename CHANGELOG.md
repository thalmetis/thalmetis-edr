# Changelog

## 0.1.0 - 2026-04-30

`thalmetis-edr` v0.1 prepares a bounded McRae 2024 Figure 5a / Table 3
pathway reconstruction for research and educational reproducibility.

Included scope:

- packaged Figure 5a-derived affected-volume data inferred from `bub80compare9.m`
- packaged published Table 3 fixture
- packaged inferred calculator `R_b` values
- spherical bubble-volume calculation
- event-count calculation from cumulative gas volume and bubble volume
- McRae Equation 3 viability arithmetic
- Table 3 pathway calculation and validation semantics
- top-level clipping reporting
- Table 3 reconciliation documentation
- README quickstart
- runnable minimal Table 3 notebook
- Table 3 example script
- GitHub Actions CI workflow for tests, lint, and example smoke execution

Explicit non-scope:

- no Equation 2 implementation
- no arbitrary EDR-threshold interpolation
- no arbitrary thread-radius interpolation
- no arbitrary bubble-radius interpolation
- no rupture viability
- no combined pinch-off + rupture viability
- no coalescence
- no path-independence
- no thesis Table 4.4
- no unpublished 2026 hemolysis work
- no ML or XGBoost
- no GUI, web, server, cloud, or API dependencies
- PyPI publication is not included in v0.1.0.

Archive:

- Archived on Zenodo: https://doi.org/10.5281/zenodo.19932774
