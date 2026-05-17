## Epic 05: Modulation System

### Backend Track

- [x] 05.B1 Audio modulator sources: support band envelopes, onset, beat pulse, beat phase, bar phase, and phrase progress.
- [x] 05.B2 Procedural modulator sources: support LFO and seeded random sources.
- [x] 05.B3 Mapping ops part 1: support scale, clamp, and invert.
- [x] 05.B4 Mapping ops part 2: support curve, smooth, lag, and quantize.
- [x] 05.B5 Preset bindings: allow presets to bind modulators to layer parameters without custom Python code.
- [x] 05.B6 Deterministic execution: make modulator outputs stable for the same analysis, seed, and time.
- [x] 05.B7 Debug output shape: expose resolved modulator values in a structured format.

### Frontend Track

- [ ] 05.F1 Modulator value types: add frontend types for current modulator values and mappings.
- [ ] 05.F2 Modulator inspection readiness: define a UI-facing shape for viewing live modulator values later.

### Validation Track

- [ ] 05.V1 Binding test: prove presets can bind modulators to layer parameters without layer-specific code.
- [ ] 05.V2 Determinism test: prove modulator outputs stay stable for the same inputs.
- [ ] 05.V3 Mapping test: prove mapping operations apply in the declared order.

