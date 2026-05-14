## Epic 06: Preset Schema

### Backend Track

- [ ] 06.B1 Preset format v1: define preset identity, version, display fields, tags, and description.
- [ ] 06.B2 Parameter schema: define typed parameters with defaults, bounds, step size, and UI grouping.
- [ ] 06.B3 Layer stack schema: let a preset declare ordered layers and per-layer params.
- [ ] 06.B4 Palette schema: let a preset declare palette and color controls.
- [ ] 06.B5 Blend schema: let a preset declare blend modes at preset or layer level.
- [ ] 06.B6 Preset validation: fail invalid presets with actionable errors before render time.
- [ ] 06.B7 Undersea waves preset: define the first preset `undersea_waves` featuring 3 layered sine waves moving left to right, restricted to parcan chase effects, with a configurable base color (default blue). The wave speed must dynamically respond to beat timing, and the wave intensity/glitter must modulate based on FFT band changes.
- [ ] 06.B8 Baseline preset migration: represent the current wave plus pulse look as preset `undersea_pulse_01`.

### Frontend Track

- [ ] 06.F1 Preset summary type: add frontend types for preset identity, labels, and tags.
- [ ] 06.F2 Parameter schema type: add frontend types for typed preset parameters and UI groups.
- [ ] 06.F3 Preset loading readiness: make the UI able to consume schema-defined presets later without hardcoded assumptions.

### Validation Track

- [ ] 06.V1 Valid preset test: prove a valid preset loads and passes schema validation.
- [ ] 06.V2 Invalid preset test: prove invalid presets fail with actionable errors.
- [ ] 06.V3 Undersea waves test: prove `undersea_waves` renders 3 layered sine waves, respects the configurable base color, limits output intensity exclusively to parcan anchor coordinates, and validates that wave speed and glitter respond to beat and FFT signals respectively.
- [ ] 06.V4 Baseline parity test: prove `undersea_pulse_01` reproduces the current baseline look closely enough.

