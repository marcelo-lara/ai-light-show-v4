## Epic 06: Preset Schema

Implementation note: use `docs/spec-preset-math-schema.md` for the concrete preset file shape and `docs/spec-expression-authoring-model.md` for the stored authoring model decision.

### Backend Track

- [ ] 06.B1 Preset format v1: define preset identity, version, display fields, tags, and description.
- [ ] 06.B2 Parameter schema: define typed parameters with defaults, bounds, step size, and UI grouping.
- [ ] 06.B3 Layer stack schema: let a preset declare ordered layers and per-layer params.
- [ ] 06.B4 Palette schema: let a preset declare palette and color controls.
- [ ] 06.B5 Blend schema: let a preset declare blend modes at preset or layer level.
- [ ] 06.B6 Preset validation: fail invalid presets with actionable errors before render time.
- [ ] 06.B7 Ocean waves preset: define the first preset `ocean_waves` using the `ocean_waves` shader to create large left-to-right swells for parcans, with a configurable deep-blue base color and controllable inner-contrast behavior. The wave speed must dynamically respond to beat timing, and the wave intensity or highlight motion must modulate based on FFT band changes.
- [ ] 06.B8 Baseline preset migration: represent the current wave plus pulse look as preset `undersea_pulse_01`.
- [ ] 06.B9 Stage-scoped math schema: allow presets or layers to declare optional `preset_init`, `frame`, and bounded `cell` or `point` programs as AST-backed formula definitions.
- [ ] 06.B10 Shared state schema: declare preset-shared registers and layer-local state lanes with explicit defaults and bounds.
- [ ] 06.B11 Validation budgets: reject free-form DSL strings, unsupported stage access, unbounded memory patterns, or hot-path constructs that violate deterministic render budgets.

### Frontend Track

- [ ] 06.F1 Preset summary type: add frontend types for preset identity, labels, and tags.
- [ ] 06.F2 Parameter schema type: add frontend types for typed preset parameters and UI groups.
- [ ] 06.F3 Preset loading readiness: make the UI able to consume schema-defined presets later without hardcoded assumptions.
- [ ] 06.F4 Math authoring metadata type: add frontend-readable grouped metadata for AST-backed stage programs and shared state definitions.

### Validation Track

- [ ] 06.V1 Valid preset test: prove a valid preset loads and passes schema validation.
- [ ] 06.V2 Invalid preset test: prove invalid presets fail with actionable errors.
- [ ] 06.V3 Ocean waves test: prove `ocean_waves` renders readable ocean-like left-to-right swells, respects the configurable deep-blue base color, limits output intensity exclusively to parcan anchor coordinates, and validates that wave speed and inner-contrast motion respond to beat and FFT signals respectively.
- [ ] 06.V4 Baseline parity test: prove `undersea_pulse_01` reproduces the current baseline look closely enough.
- [ ] 06.V5 Stage handoff test: prove preset math blocks observe the intended init, frame, and hot-path state handoff.
- [ ] 06.V6 Budget validation test: prove invalid hot-path constructs fail before render time with actionable errors.

