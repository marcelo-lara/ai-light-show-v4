## Epic 01: Render Contract

### Backend Track

- [ ] 01.B1 Artifact schema v1: add `schema_version`, `render_id`, `preset_id`, `preset_version`, `seed`, `params`, `song_id`, `analysis_id`, `fps`, `duration`, and `frame_count` to the render artifact.
- [ ] 01.B2 Render id rules: generate a stable `render_id` from reproducible inputs instead of a random export id.
- [ ] 01.B3 Seed rules: make seed handling explicit and required in the render contract.
- [ ] 01.B4 Backend compatibility checks: reject missing required fields and unsupported schema versions.
- [ ] 01.B5 Current song state: add backend-owned `current_song` and `current_canvas` state to the playback contract.
- [ ] 01.B6 Empty canvas state: define the contract for a loaded song with no current canvas yet.
- [ ] 01.B7 Chunked binary frames: split v2 frame payloads into short binary chunks stored in `data/artifacts/` instead of one monolithic `.bin` file to reduce memory pressure and enable progressive loading later.

### Frontend Track

- [ ] 01.F1 Shared artifact type: define frontend types that match the backend render artifact contract.
- [ ] 01.F2 Frontend compatibility state: reject incompatible artifacts with a clear UI error state.
- [ ] 01.F3 Metadata display readiness: surface schema version, render id, preset id, and seed in a way the UI can consume.
- [ ] 01.F4 Current state types: add frontend types for backend-owned `current_song`, `current_canvas`, and empty-canvas states.

### Validation Track

- [ ] 01.V1 Deterministic render test: prove the same song, preset, params, and seed produce identical frames.
- [ ] 01.V2 Stable render id test: prove the same inputs produce the same `render_id`.
- [ ] 01.V3 Golden sample fixture: add one short canonical render artifact for regression checks.
- [ ] 01.V4 Empty canvas contract test: prove a song can load without an existing canvas or show.
- [ ] 01.V5 v1/v2 parity test: add a regression test that loads a short fixture as both legacy JSON frames and v2 binary frames and proves the decoded pixels match exactly.

