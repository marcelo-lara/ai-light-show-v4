## Epic 11: Fixture Mapping And Export

### Backend Track

- [ ] 11.B1 Canonical pixel order: document and encode the canonical origin and row-major pixel order.
- [ ] 11.B2 Fixture reference schema: treat `data/fixtures/fixtures.json` as real fixture instances with fixture-type id and normalized canvas location.
- [ ] 11.B3 POI reference schema: treat `data/fixtures/pois.json` as normalized points of interest with optional per-fixture pan and tilt calibration targeting `ref_0_0_0`.
- [ ] 11.B4 Mapping config: define fixture or layout mapping inputs.
- [ ] 11.B5 Linear mapping: support linear pixel order.
- [ ] 11.B6 Serpentine mapping: support serpentine pixel order.
- [ ] 11.B7 Export manifest v1: export mapped frame metadata without changing the canonical render artifact.
- [ ] 11.B8 Gamma correction: add gamma correction to export.
- [ ] 11.B9 Brightness limiting: add brightness limiting to export.

### Frontend Track

- [ ] 11.F1 Export metadata types: add frontend types for export and mapping metadata.
- [ ] 11.F2 Export review readiness: make the UI able to inspect export metadata and mapping results later.
- [ ] 11.F3 Fixture and POI reference types: add frontend-readable types for fixture instances and POIs.

### Validation Track

- [ ] 11.V1 Orientation test pattern: add a test pattern that makes orientation obvious.
- [ ] 11.V2 Ordering test pattern: add a test pattern that makes pixel ordering obvious.
- [ ] 11.V3 Mapping validation: add validation checks for orientation, ordering, and layout mapping.

