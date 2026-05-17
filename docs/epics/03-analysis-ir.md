## Epic 03: Analysis IR

### Backend Track

- [x] 03.B1 Analysis schema v1: version the analysis cache and invalidate it when analyzer logic changes.
- [x] 03.B2 Beat timing signals: add `beat_phase` and nearest-beat distance to timestamp queries.
- [x] 03.B3 Bar timing signal: add `bar_phase` to timestamp queries.
- [x] 03.B4 Smoothed envelopes: add smoothed per-band envelopes.
- [x] 03.B5 Global energy: add a normalized global energy curve.
- [x] 03.B6 Musical structure: add downbeat, phrase, and section candidates with confidence values.
- [x] 03.B7 Analysis diagnostics: expose confidence, source metadata, and basic debug stats in the analysis artifact.

### Frontend Track

- [x] 03.F1 Analysis type updates: add types for beat phase, bar phase, energy, and structure metadata.
- [x] 03.F2 Analysis debug readiness: expose analysis metadata in a shape the UI can inspect later.

### Validation Track

- [x] 03.V1 Cache invalidation test: prove analyzer schema changes invalidate cached analysis.
- [x] 03.V2 Timestamp query test: prove beat phase, bar phase, and nearest-beat fields are available at render time.
- [x] 03.V3 Signal sanity test: verify smoothed envelopes and energy values stay normalized and bounded.

