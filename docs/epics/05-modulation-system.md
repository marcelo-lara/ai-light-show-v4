## Epic 05: Modulation System

### Backend Track

- [ ] 05.B1 Audio modulator sources: support band envelopes, onset, beat pulse, beat phase, bar phase, and phrase progress.
- [ ] 05.B2 Procedural modulator sources: support LFO and seeded random sources.
- [ ] 05.B3 Mapping ops part 1: support scale, clamp, and invert.
- [ ] 05.B4 Mapping ops part 2: support curve, smooth, lag, and quantize.
- [ ] 05.B5 Preset bindings: allow presets to bind modulators to layer parameters without custom Python code.
- [ ] 05.B6 Deterministic execution: make modulator outputs stable for the same analysis, seed, and time.
- [ ] 05.B7 Debug output shape: expose resolved modulator values in a structured format.
- [ ] 05.B8 Staged math contexts: define bounded `preset_init`, `frame`, and optional hot-path `cell` or `point` execution contexts for expression-driven behavior.
- [ ] 05.B9 Shared state lanes: define deterministic preset-shared registers and layer-local state lanes for passing derived values across stages.
- [ ] 05.B10 Hot-path guardrails: validate that hot-path math stays bounded, deterministic, and cheap enough for `100x50` precompute rendering.

### Frontend Track

- [ ] 05.F1 Modulator value types: add frontend types for current modulator values and mappings.
- [ ] 05.F2 Modulator inspection readiness: define a UI-facing shape for viewing live modulator values later.

### Validation Track

- [ ] 05.V1 Binding test: prove presets can bind modulators to layer parameters without layer-specific code.
- [ ] 05.V2 Determinism test: prove modulator outputs stay stable for the same inputs.
- [ ] 05.V3 Mapping test: prove mapping operations apply in the declared order.
- [ ] 05.V4 Context ordering test: prove staged math contexts execute in the intended `preset_init` then `frame` then hot-path order.
- [ ] 05.V5 Shared state test: prove register and local state handoff is deterministic and bounded.

