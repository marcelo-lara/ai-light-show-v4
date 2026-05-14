## Epic 09: Timeline Director

### Backend Track

- [ ] 09.B1 Scene model: define scene fields for `start`, `end`, `preset_id`, `params`, `seed`, and `intensity`.
- [ ] 09.B2 Auto timeline from sections: generate a first-pass timeline from detected sections.
- [ ] 09.B3 Auto timeline from phrases or beats: support fallback scene generation from phrase or beat grouping.
- [ ] 09.B4 Scene overrides: support manual scene edits without breaking auto-generated defaults.
- [ ] 09.B5 Scene automation: support scene-level intensity automation.
- [ ] 09.B6 Param automation: support scene-level parameter automation.
- [ ] 09.B7 Artifact integration: include timeline metadata in render artifacts.

### Frontend Track

- [ ] 09.F1 Timeline types: add frontend types for scenes, ranges, and automation metadata.
- [ ] 09.F2 Timeline display readiness: make the UI able to consume timeline metadata later.

### Validation Track

- [ ] 09.V1 Multi-scene render test: prove one song can render with multiple scenes.
- [ ] 09.V2 Alignment test: prove scene boundaries align to beats or phrases by default.
- [ ] 09.V3 Override test: prove manual scene overrides persist over auto-generated defaults.

