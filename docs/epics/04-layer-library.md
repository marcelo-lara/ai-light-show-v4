## Epic 04: Layer Library

Implementation note: use `docs/spec-bouncing-ball-test-shader.md` for the first deterministic renderer-calibration shader.

### Backend Track

- [ ] 04.B1 Layer interface: define a registry-based layer API with deterministic seeded execution and load backend shader modules from `backend/shaders/`.
- [ ] 04.B2 Wave layer migration: convert wave into a reusable registry-backed layer.
- [ ] 04.B3 Radial pulse migration: convert radial pulse into a reusable registry-backed layer.
- [ ] 04.B4 Solid field layer: add a solid fill layer.
- [ ] 04.B5 Gradient field layer: add a gradient layer.
- [ ] 04.B6 Bars layer: add horizontal or vertical bars.
- [ ] 04.B7 Rings layer: add ring or expanding pulse output.
- [ ] 04.B8 Beat flash layer: add a beat flash layer.
- [ ] 04.B9 Scanner layer: add a scanner or sweep layer.
- [ ] 04.B10 Mirror transform: add mirror or symmetry transforms.
- [ ] 04.B11 Blend ops: add `max`, `add`, `alpha`, `multiply`, `screen`, `difference`, and `mask`.
- [ ] 04.B12 Scroll and zoom transforms: add scroll and zoom transforms.
- [ ] 04.B13 Bouncing ball test shader: add a deterministic single-point `bouncing_ball` shader in `backend/shaders/` that reflects at canvas bounds for render sanity checks.

### Frontend Track

- [ ] 04.F1 Layer metadata type: add frontend-readable layer ids, labels, and parameter schemas.
- [ ] 04.F2 Layer fixture browsing readiness: define a simple UI-facing shape for inspecting available layers later.
- [ ] 04.F3 Test shader preview readiness: expose `bouncing_ball` in a way the frontend can select and preview it as a render-validation look.

### Validation Track

- [ ] 04.V1 Registry test: prove layers are registered and loadable by id.
- [ ] 04.V2 Determinism test: prove seeded layers render reproducibly.
- [ ] 04.V3 Visual fixture coverage: add at least one fixture or snapshot test per layer.
- [ ] 04.V4 Bouncing ball path test: prove the point follows a deterministic path and reflects at the expected canvas edges.
- [ ] 04.V5 Bouncing ball preview test: prove the frontend preview shows the same bounce path and edge collisions as the backend render artifact.

