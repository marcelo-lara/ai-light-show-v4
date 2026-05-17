## Epic 08: Spectroid Chase Shader

### Backend Track

- [x] 08.B1 Central spectroid signal: define the analysis input for central spectroid, note, or chord-reactive triggering.
- [x] 08.B2 Chase layer spec: define a note or chord-reactive shader named `spectroid_chase`.
- [x] 08.B3 Parcan anchor selection: use parcan fixture positions as chase origin anchors on the canvas.
- [x] 08.B4 Chase path generation: generate outward line motion from parcan anchors toward the canvas.
- [x] 08.B5 Moving head follow lines: define line-follow behavior that moving heads can track visually later.
- [x] 08.B6 Parameter schema: define controls for trigger sensitivity, line length, spread, fade, and chase speed.
- [x] 08.B7 Preset integration: make the shader usable from the preset and layer system.

### Frontend Track

- [x] 08.F1 Shader metadata types: add frontend-readable types for the `spectroid_chase` shader and its parameter schema.
- [x] 08.F2 Fixture-anchor readiness: make the UI able to consume parcan-anchor and moving-head-line controls later.
- [x] 08.F3 Overlay compatibility: ensure fixture and POI overlays remain useful while previewing the chase shader.

### Validation Track

- [x] 08.V1 Trigger response test: prove the shader reacts deterministically to the central spectroid or note/chord signal.
- [x] 08.V2 Parcan anchor test: prove chase lines start from parcan positions.
- [x] 08.V3 Line-follow test: prove outward line motion is stable and visually trackable for moving-head follow behavior.
- [x] 08.V4 Snapshot test: add at least one visual fixture or snapshot test for the spectroid chase shader.

