# MVP acceptance criteria

The MVP is a **policy compiler and capability auditor**, not yet a forecasting product.

## Done when

- a versioned, source-attributed corpus can be loaded;
- every measure compiles to a typed `PolicyObject`;
- unsupported measures become explicit gaps;
- structural reforms can request institutional/scenario capabilities;
- quantitative parameters are retained when present;
- an audit reports classification, traceability, gaps and required capabilities;
- automated tests protect the non-invention rule;
- CI runs tests on every push and pull request.

## Not claimed by this MVP

The current engine does **not** claim validated causal estimates of GDP, employment, crime, health, migration, diplomatic reactions or electoral outcomes. Those require separately validated model adapters and data.
