## Epic 07: Raindrops Shader

### Backend Track

- [x] 07.B1 Raindrops layer spec: define a POI-aware radial pulse layer named `raindrops`.
- [x] 07.B2 POI source selection: allow pulses to start from one or more configured POIs.
- [x] 07.B3 POI transit behavior: allow pulses to pass through configured POIs on the canvas.
- [x] 07.B4 POI collision behavior: allow pulses to collide at configured POIs and create a visible interaction.
- [x] 07.B5 Parameter schema: define controls for pulse rate, radius growth, decay, collision strength, and POI selection.
- [x] 07.B6 Preset integration: make the raindrops shader usable from the preset and layer system.

### Frontend Track

- [x] 07.F1 Shader metadata types: add frontend-readable types for the `raindrops` shader and its parameter schema.
- [x] 07.F2 POI selection readiness: make the UI able to consume POI-backed shader controls later.
- [x] 07.F3 Overlay compatibility: ensure the fixture and POI reference overlay remains useful while previewing raindrops output.

### Validation Track

- [x] 07.V1 POI start test: prove pulses can originate from configured POIs.
- [x] 07.V2 POI transit test: prove pulses can pass through intermediate POIs.
- [x] 07.V3 POI collision test: prove two or more pulses can collide at a POI and produce deterministic output.
- [x] 07.V4 Snapshot test: add at least one visual fixture or snapshot test for the raindrops shader.

