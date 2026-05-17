# Development Handoff Stories

Use these as small implementation handoff units. Each story should fit one focused PR or one focused LLM task.

Treat this file as the implementation router, not the full spec. Before starting a story, read the dependency notes and the linked source-of-truth docs for that slice.

## Handoff Spec

- Frontend dev port: `3400`.
- Backend API port: `3401`.
- Backend shader implementations target `backend/shaders/`.
- Preset source files target `backend/presets/`.
- Implementation should happen in this repo. If the backend or frontend trees do not exist yet, scaffold them here before feature stories.
- Organic visual behavior should come from deterministic staged math and bounded shared state, not imported BeatDrop runtime code.
- `data/songs/` is read-only input storage; generated backend outputs must not be written there.
- All generated artifacts and persistent render metadata live under `data/artifacts/`.
- Persistent review, approval, and other non-transient render status must be stored in artifact metadata under `data/artifacts/`.
- Split work into backend, frontend, and validation tracks.
- Story ids stay stable even if list order changes.
- Prefer smaller stories over broad multi-surface stories.
- Use `show name` as the UI label, but persist it as `canvas_name`; unless a story says otherwise, `show` and `canvas` refer to the same saved render selection.
- The server owns `current_song` and `current_canvas` state.
- The server also owns the available canvas list for the current song.
- The server also owns the current playback transport state and current render session state.
- There is exactly one active song, one active canvas, and one active render session for the whole system at a time.
- The frontend should request song changes from the backend instead of loading songs directly.
- The frontend song loader is a dropdown populated from the backend-visible contents of `data/songs/`.
- When a new song is loaded, the backend should return or push the updated current song, current canvas, and available canvas list to the frontend.
- When a song has no saved canvases, `current_canvas` is `null` and the canvas dropdown is empty.
- When a song has saved canvases, the frontend displays a backend-driven canvas dropdown and any selection change must go through the shared backend session.
- Playback transport uses explicit `Play`, `Pause`, and `Stop` controls driven by backend-owned state.
- Shared-session fanout uses WebSocket transport.
- When one client changes the song, canvas, render, or transport state, all other connected clients should follow that shared server state instead of keeping private local playback state.
- If the current song has no canvas or show yet, the song should still load successfully; canvas creation happens only when the user triggers `Render`.
- The left control column uses tabs: one `Main` tab for render-scoped controls (`show name`, preset checklist, and `Render`), then one tab per active shader or layer property group.
- Runtime validation must use Docker, not host-local service startup.
- Before browser validation, run `docker compose down` then `docker compose up -d --build` from the repo root.
- Browser validation must hit the real app in Docker through the documented ports, not mocked APIs or mocked canvas data.
- Use `data/songs/What a Feeling - Courtney Storm.mp3` as the default end-to-end preview validation song unless a story explicitly names a different fixture.
- Use `docs/spec-browser-visual-regression.md` as the named browser-case inventory for visual regression coverage.
- Use `docs/spec-bouncing-ball-test-shader.md` as the source of truth for the first renderer-calibration shader.
- Use `docs/spec-ocean-waves-shader.md` as the source of truth for the parcan-first ocean-wave look.
- The epic order below is roadmap order. If a story-level dependency note below conflicts with the epic order, follow the story-level dependency note.

## Read Before Starting

- Render contract and artifact layout: [phase-01-baseline-and-contracts.md](./phases/phase-01-baseline-and-contracts.md), [01-render-contract.md](./epics/01-render-contract.md), and [spec-data-schemas.md](./spec-data-schemas.md).
- Preview console and browser validation: [02-preview-console.md](./epics/02-preview-console.md), [phase-05-production-console.md](./phases/phase-05-production-console.md), and [spec-browser-visual-regression.md](./spec-browser-visual-regression.md).
- Analysis and reusable modulation signals: [phase-02-musical-analysis-ir.md](./phases/phase-02-musical-analysis-ir.md), [03-analysis-ir.md](./epics/03-analysis-ir.md), and [05-modulation-system.md](./epics/05-modulation-system.md).
- Preset and layer engine: [phase-03-preset-and-layer-engine.md](./phases/phase-03-preset-and-layer-engine.md), [04-layer-library.md](./epics/04-layer-library.md), [06-preset-schema.md](./epics/06-preset-schema.md), [spec-expression-authoring-model.md](./spec-expression-authoring-model.md), and [spec-preset-math-schema.md](./spec-preset-math-schema.md).
- Renderer-calibration and ocean-wave features: [spec-bouncing-ball-test-shader.md](./spec-bouncing-ball-test-shader.md) and [spec-ocean-waves-shader.md](./spec-ocean-waves-shader.md).
- Timeline and transitions: [phase-04-timeline-and-direction.md](./phases/phase-04-timeline-and-direction.md), [09-timeline-director.md](./epics/09-timeline-director.md), and [10-transition-system.md](./epics/10-transition-system.md).

## Current Repo Reality

- The current workspace snapshot contains docs and data, but not a checked-in `backend/` or `frontend/` implementation tree.
- Build the implementation in this repo; do not split these stories into a separate codebase.
- If no implementation tree exists yet, add one bootstrap task in this repo for backend, frontend, Docker wiring, and shared API scaffolding before feature stories. Do not create those foundations ad hoc inside unrelated stories.

## Story-Level Dependency Rules

- Epic 01 is the contract floor for shared song, canvas, render, and playback state. Do not build client-specific state semantics that bypass it.
- Epic 02 is not one indivisible batch. Start with song loading, render triggering, shared-session flow, canvas-dropdown selection, overlays, and progress basics. Defer preset-driven tabs until Epic 06, timeline UI until Epics 09 and 10, chunked-artifact preview until 01.B7, and `bouncing_ball` preview validation until 04.B13 and 04.F3.
- Epic 03 supplies the musical signals consumed by Epic 05. Do not implement beat, bar, phrase, or section-driven modulators before 03.B2 through 03.B6 land.
- Epic 04 supplies the shader registry and reusable layer ids consumed by Epic 06. Do not implement production presets against ad hoc shader wiring.
- Epic 05 and Epic 06 share one authored-math design surface. Read [spec-expression-authoring-model.md](./spec-expression-authoring-model.md) and [spec-preset-math-schema.md](./spec-preset-math-schema.md) before touching 05.B8 through 05.B10 or 06.B9 through 06.B11.
- 06.B7 and 06.V3 depend on the `ocean_waves` shader behavior from Epic 13 plus modulation signals from Epics 03 and 05. Implement those stories with Epic 13, not before it.
- Epics 07, 08, and 13 depend on Epic 04 registry integration, Epic 05 modulation behavior, Epic 06 preset/schema wiring, and fixture or POI definitions from `data/fixtures/`.
- Epic 10 depends on Epic 09 scene and timeline metadata. Do not invent standalone transition storage that later has to be migrated.
- Epic 11 depends on the artifact contract from Epic 01 and the fixture or POI file shapes from [spec-data-schemas.md](./spec-data-schemas.md).
- Epic 12 should lock baselines only after the underlying surface is stable enough to be deterministic. Do not start regression capture on stories that are still changing their payload shape or UI layout every pass.

## Locked Decisions

- Implementation location: build the backend and frontend in this repo.
- Shared-session transport: use WebSocket for backend fanout and multi-client follow behavior.
- Canvas selection model: expose the current song's available canvases as a dropdown list; when none exist, keep the list empty and `current_canvas` null.
- Persistent status model: store approval and other non-transient render-status metadata under `data/artifacts/` as artifact metadata.

## Implementation Order

1. Epic 01: Render Contract
2. Epic 02: Preview Console
3. Epic 03: Analysis IR
4. Epic 04: Layer Library
5. Epic 05: Modulation System
6. Epic 06: Preset Schema
7. Epic 07: Raindrops Shader
8. Epic 08: Spectroid Chase Shader
9. Epic 09: Timeline Director
10. Epic 10: Transition System
11. Epic 11: Fixture Mapping And Export
12. Epic 12: Render Diagnostics
13. Epic 13: Ocean Waves Shader

## Epic 01: Render Contract

### Backend Track

- [ ] 01.B1 Artifact schema v1: add `schema_version`, `render_id`, `preset_id`, `preset_version`, `seed`, `params`, `song_id`, `analysis_id`, `fps`, `duration`, `frame_count`, and a persistent `status` block to the render artifact metadata.
- [ ] 01.B2 Render id rules: generate a stable `render_id` from reproducible inputs instead of a random export id.
- [ ] 01.B3 Seed rules: make seed handling explicit and required in the render contract.
- [ ] 01.B4 Backend compatibility checks: reject missing required fields and unsupported schema versions.
- [ ] 01.B5 Current song state: add backend-owned `current_song`, `current_canvas`, and `available_canvases` state to the playback contract.
- [ ] 01.B6 Empty canvas state: define the contract for a loaded song with no current canvas yet, including `current_canvas: null` and an empty available-canvas list.
- [ ] 01.B7 Chunked binary frames: split v2 frame payloads into short binary chunks stored in `data/artifacts/` instead of one monolithic `.bin` file to reduce memory pressure and enable progressive loading later.
- [ ] 01.B8 Shared playback state contract: add backend-owned playback transport fields for `stopped`, `paused`, `playing`, current playback time, and playback owner-neutral synchronization semantics.
- [ ] 01.B9 Singleton session contract: define that `current_song`, `current_canvas`, and the active render job are global shared session state, not per-client selections.

### Frontend Track

- [ ] 01.F1 Shared artifact type: define frontend types that match the backend render artifact contract.
- [ ] 01.F2 Frontend compatibility state: reject incompatible artifacts with a clear UI error state.
- [ ] 01.F3 Metadata display readiness: surface schema version, render id, preset id, seed, and persistent status in a way the UI can consume.
- [ ] 01.F4 Current state types: add frontend types for backend-owned `current_song`, `current_canvas`, `available_canvases`, and empty-canvas states.
- [ ] 01.F5 Shared playback state types: add frontend types for backend-owned playback transport and shared-session state.

### Validation Track

- [ ] 01.V1 Deterministic render test: prove the same song, preset, params, and seed produce identical frames.
- [ ] 01.V2 Stable render id test: prove the same inputs produce the same `render_id`.
- [ ] 01.V3 Golden sample fixture: add one short canonical render artifact for regression checks.
- [ ] 01.V4 Empty canvas contract test: prove a song can load without an existing canvas or show and returns `current_canvas: null` plus an empty available-canvas list.
- [ ] 01.V5 v1/v2 parity test: add a regression test that loads a short fixture as both legacy JSON frames and v2 binary frames and proves the decoded pixels match exactly.
- [ ] 01.V6 Shared session contract test: prove multiple clients receive the same current song, current canvas, available canvas list, render job, and playback transport state over WebSocket.

## Epic 02: Preview Console

### Backend Track

- [ ] 02.B1 Song load endpoint: add one backend action that sets the current song and returns the updated current song, current canvas, and available canvas list.
- [ ] 02.B2 Missing canvas on load: make song-load succeed even when no show exists for that song, returning `current_canvas: null` and an empty canvas list.
- [ ] 02.B3 Render action contract: make `Render` create or replace the current canvas for the already loaded song.
- [ ] 02.B4 Metadata payload support: expose artifact metadata needed by the console, including persistent status fields, without UI-only assumptions.
- [ ] 02.B5 Generation status payload: expose render job status, progress, and failure details through the API.
- [ ] 02.B6 Analysis phase progress: expose analysis-stage progress and status text before frame rendering begins.
- [ ] 02.B7 Render progress cadence: publish render progress with current and total frame counts at least every `200` frames.
- [ ] 02.B8 Canvas naming contract: accept a user-provided canvas name and persist exports as `{song_name}.{canvas_name}.json`.
- [ ] 02.B9 Progress phase payload wiring: extend job status so the API reports analysis vs render phase and enough numeric progress for the frontend progress bar to reflect the active phase.
- [ ] 02.B10 Song catalog endpoint: expose the available song list derived from `data/songs/` for a frontend dropdown selector.
- [ ] 02.B11 Playback transport actions: add backend actions for `Play`, `Pause`, and `Stop` against the shared current canvas playback state.
- [ ] 02.B12 Shared-state fanout: push or broadcast song, available canvas list, canvas, render, and playback-state updates to all connected clients over WebSocket.
- [ ] 02.B13 Global render-session rule: reject per-client private song or canvas selection semantics and keep one active shared render target at a time.
- [ ] 02.B14 Canvas selection action: add one backend action that sets the shared `current_canvas` from the current song's available canvas list.
- [ ] 02.B15 Approval metadata persistence: store and update render approval state in artifact metadata under `data/artifacts/`.

### Frontend Track

- [ ] 02.F1 Console network spec: update the frontend to target port `3400` and the backend API on port `3401`.
- [ ] 02.F2 Server-owned song flow: request song changes from the backend instead of loading song files directly in the frontend.
- [ ] 02.F3 Song-loaded UI update: update the frontend when the backend reports a new current song, current canvas, and available canvas list.
- [ ] 02.F4 Empty canvas state UI: allow a song to be loaded and preview-ready even when no show exists yet, with an empty canvas dropdown.
- [ ] 02.F5 Main tab shell: add a `Main` tab in the left column as the home for render-scoped controls.
- [ ] 02.F6 Shader tabs: add one left-column tab per active shader or layer property group.
- [ ] 02.F24 Main tab preset checklist: in the `Main` tab, add a `show name` input that defaults to overwrite mode and a checklist of presets to include in the render.
- [ ] 02.F25 Preset tab visibility control: show one preset-parameter tab per checked preset and hide tabs for unchecked presets before applying to the canvas.
- [ ] 02.F7 Fixture overlay load: load fixture references from `data/fixtures/fixtures.json`.
- [ ] 02.F8 POI overlay load: load POI references from `data/fixtures/pois.json`.
- [ ] 02.F9 Canvas reference overlay: draw fixtures and POIs as a visual overlay on the canvas.
- [ ] 02.F10 Overlay marker styling: make fixture markers visually distinct from POI markers.
- [ ] 02.F11 Artifact metadata panel: show render metadata, schema version, preset id, seed, and compatibility state.
- [ ] 02.F12 Generation workflow UI: show render job status, progress, and failure details.
- [ ] 02.F13 Preset-driven controls: build shader or layer controls from schema-defined groups instead of hardcoded controls.
- [ ] 02.F14 Timeline view: add timeline display for scene and transition metadata.
- [ ] 02.F15 Frame inspector: add pixel inspection with coordinates and RGB values.
- [ ] 02.F16 Fullscreen preview: add fullscreen preview while preserving `100x50` pixel character.
- [ ] 02.F17 A/B compare: add compare mode between two renders.
- [ ] 02.F18 Approval workflow: add render approval status in the UI.
- [ ] 02.F19 Full-width canvas fit: scale the preview canvas to the full available content width while preserving the render aspect ratio.
- [ ] 02.F20 Generating progress bar: show render progress as a progress bar behind the `Generating...` label instead of text-only status.
- [ ] 02.F21 Canvas name input: add a textbox for the canvas name used when `Render` creates `{song_name}.{canvas_name}.json`.
- [ ] 02.F22 Header canvas-only title: show only the current canvas name in the header and hide the redundant song-name text there.
- [ ] 02.F23 Phase-aware progress UI: drive the `Generating...` progress bar from the backend's analysis/render phase payload instead of a generic polling state.
- [ ] 02.F26 Song loader dropdown: render a single song selector dropdown populated from the backend song catalog sourced from `data/songs/`.
- [ ] 02.F27 Playback transport controls: add `Play`, `Pause`, and `Stop` buttons for canvas playback in the review console.
- [ ] 02.F28 Shared-session follow mode: when another client changes the active song, canvas, render, or playback transport state, update this client to match the server-owned session.
- [ ] 02.F29 Test shader preview flow: allow the `bouncing_ball` render to be previewed cleanly as a renderer-validation look without requiring production-only preset complexity.
- [ ] 02.F30 Canvas dropdown: show the current song's available canvases in a dropdown, keep it empty when none exist, and route selection changes through the backend-owned shared session.

### Validation Track

- [ ] 02.V1 Port configuration check: prove the frontend and backend run on the documented ports `3400` and `3401`.
- [ ] 02.V2 Schema error state test: prove incompatible artifacts show a clear UI state.
- [ ] 02.V3 Song load flow test: prove the frontend asks the backend to load a song and updates when the backend confirms the new current song.
- [ ] 02.V4 Missing canvas flow test: prove a song with no canvas still loads and only creates a show on `Render`.
- [ ] 02.V5 Left-tab layout test: prove the left column shows one `Main` tab and one tab per active shader or layer group.
- [ ] 02.V6 Overlay load test: prove fixtures and POIs load from their JSON files and render as overlay references.
- [ ] 02.V7 Overlay alignment test: prove fixture and POI markers stay aligned to canvas coordinates.
- [ ] 02.V8 Review workflow test: prove a user can load a song, render a show, inspect it, and approve it from the UI.
- [ ] 02.V9 Full-width preview test: prove the canvas expands to the available width without distorting the render aspect ratio.
- [ ] 02.V10 Canvas name render test: prove the entered canvas name is sent to the backend and the resulting canvas file uses `{song_name}.{canvas_name}.json`.
- [ ] 02.V11 Progress phase test: prove the UI distinguishes analysis progress from render progress and updates render progress every `200` frames.
- [ ] 02.V12 Chunk compatibility flow test: prove the preview can still load and play a chunked v2 canvas artifact without changing current-canvas selection semantics.
- [ ] 02.V13 Preset tab selection flow test: prove the `Main` tab shows overwrite-default `show name` input plus preset checklist, and that selecting presets shows only those preset parameter tabs while unselected preset tabs remain hidden before render.
- [ ] 02.V14 Docker browser smoke test: run `docker compose down` then `docker compose up -d --build`, open the live preview in a real browser, load `data/songs/What a Feeling - Courtney Storm.mp3`, trigger `Render`, and verify the resulting canvas, overlays, and review workflow without mocked backend responses.
- [ ] 02.V15 Song dropdown test: prove the frontend song loader is a dropdown populated from the backend view of `data/songs/`.
- [ ] 02.V16 Playback controls test: prove `Play`, `Pause`, and `Stop` drive the shared backend playback state and update the canvas preview accordingly.
- [ ] 02.V17 Multi-client follow test: prove when one client changes the song, canvas, render, or playback transport state, other connected clients follow the same shared session over WebSocket.
- [ ] 02.V18 Bouncing ball preview test: prove a rendered `bouncing_ball` canvas displays a single crisp point moving and bouncing at the expected edges in the frontend preview.
- [ ] 02.V19 Canvas dropdown selection test: prove when a song has multiple canvases the dropdown shows the available list, when none exist it stays empty, and selecting a canvas updates the shared `current_canvas` across WebSocket-connected clients.
- [ ] 02.V20 Approval metadata test: prove approval state changes persist in artifact metadata under `data/artifacts/` and render correctly in the console.

## Epic 03: Analysis IR

### Backend Track

- [ ] 03.B1 Analysis schema v1: version the analysis cache and invalidate it when analyzer logic changes.
- [ ] 03.B2 Beat timing signals: add `beat_phase` and nearest-beat distance to timestamp queries.
- [ ] 03.B3 Bar timing signal: add `bar_phase` to timestamp queries.
- [ ] 03.B4 Smoothed envelopes: add smoothed per-band envelopes.
- [ ] 03.B5 Global energy: add a normalized global energy curve.
- [ ] 03.B6 Musical structure: add downbeat, phrase, and section candidates with confidence values.
- [ ] 03.B7 Analysis diagnostics: expose confidence, source metadata, and basic debug stats in the analysis artifact.

### Frontend Track

- [ ] 03.F1 Analysis type updates: add types for beat phase, bar phase, energy, and structure metadata.
- [ ] 03.F2 Analysis debug readiness: expose analysis metadata in a shape the UI can inspect later.

### Validation Track

- [ ] 03.V1 Cache invalidation test: prove analyzer schema changes invalidate cached analysis.
- [ ] 03.V2 Timestamp query test: prove beat phase, bar phase, and nearest-beat fields are available at render time.
- [ ] 03.V3 Signal sanity test: verify smoothed envelopes and energy values stay normalized and bounded.

## Epic 04: Layer Library

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

## Epic 06: Preset Schema

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
- [ ] 06.V3 Ocean waves test: prove `ocean_waves` renders readable ocean-like left-to-right swells, respects the configurable deep-blue base color, preserves the parcan-first sampling behavior defined in [spec-ocean-waves-shader.md](./spec-ocean-waves-shader.md), and validates that wave speed and inner-contrast motion respond to beat and FFT signals respectively.
- [ ] 06.V4 Baseline parity test: prove `undersea_pulse_01` reproduces the current baseline look closely enough.
- [ ] 06.V5 Stage handoff test: prove preset math blocks observe the intended init, frame, and hot-path state handoff.
- [ ] 06.V6 Budget validation test: prove invalid hot-path constructs fail before render time with actionable errors.

## Epic 13: Ocean Waves Shader

### Backend Track

- [ ] 13.B1 Ocean waves layer spec: define a parcan-oriented shader named `ocean_waves` in `backend/shaders/`.
- [ ] 13.B2 Left-to-right swell motion: make the dominant wave bodies travel from left to right across the canvas.
- [ ] 13.B3 Three-field composition: use exactly three layered fields in v1 for primary swell mass, depth contrast, and restrained crest emphasis.
- [ ] 13.B4 Ocean palette defaults: define deep-blue base, darker troughs, and restrained cyan-highlight behavior.
- [ ] 13.B5 Contrast shaping: prefer smoothed contrast functions such as `mix`, `smoothstep`, and `clamp` over noisy or hard-thresholded crest logic.
- [ ] 13.B6 Parcan sampling intent: shape the look so broad swells remain readable when sampled by fixed parcan anchor coordinates.
- [ ] 13.B7 Parameter schema: define controls for `base_color`, `highlight_color`, `wave_speed`, `wave_scale`, `contrast_depth`, `foam_intensity`, and `parcan_only`.
- [ ] 13.B8 Preset integration: make the shader usable from the preset and layer system, including the `ocean_waves` preset.

### Frontend Track

- [ ] 13.F1 Shader metadata types: add frontend-readable types for the `ocean_waves` shader and its parameter schema.
- [ ] 13.F2 Parcan preview readiness: make the UI able to preview ocean-wave output as a parcan-first look.
- [ ] 13.F3 Contrast review readiness: ensure the preview preserves large swell readability and inner-contrast structure.

### Validation Track

- [ ] 13.V1 Direction test: prove the dominant motion reads left to right.
- [ ] 13.V2 Swell scale test: prove the output contains large wave bodies rather than high-frequency ripples.
- [ ] 13.V3 Contrast structure test: prove each swell contains readable interior contrast rather than a flat body fill.
- [ ] 13.V4 Parcan readability test: prove parcan-sampled output preserves the ocean-wave motion and internal contrast.
- [ ] 13.V5 Exact preset payload test: prove the canonical `ocean_waves` preset loads with the documented payload and defaults.
- [ ] 13.V6 Browser regression test: add browser-visible regression coverage for baseline swell readability, left-to-right movement, and inner contrast.

## Epic 07: Raindrops Shader

### Backend Track

- [ ] 07.B1 Raindrops layer spec: define a POI-aware radial pulse layer named `raindrops` in `backend/shaders/`.
- [ ] 07.B2 POI source selection: allow pulses to start from one or more configured POIs.
- [ ] 07.B3 POI transit behavior: allow pulses to pass through configured POIs on the canvas.
- [ ] 07.B4 POI collision behavior: allow pulses to collide at configured POIs and create a visible interaction.
- [ ] 07.B5 Parameter schema: define controls for pulse rate, radius growth, decay, collision strength, and POI selection.
- [ ] 07.B6 Preset integration: make the raindrops shader usable from the preset and layer system.

### Frontend Track

- [ ] 07.F1 Shader metadata types: add frontend-readable types for the `raindrops` shader and its parameter schema.
- [ ] 07.F2 POI selection readiness: make the UI able to consume POI-backed shader controls later.
- [ ] 07.F3 Overlay compatibility: ensure the fixture and POI reference overlay remains useful while previewing raindrops output.

### Validation Track

- [ ] 07.V1 POI start test: prove pulses can originate from configured POIs.
- [ ] 07.V2 POI transit test: prove pulses can pass through intermediate POIs.
- [ ] 07.V3 POI collision test: prove two or more pulses can collide at a POI and produce deterministic output.
- [ ] 07.V4 Snapshot test: add at least one visual fixture or snapshot test for the raindrops shader.

## Epic 08: Spectroid Chase Shader

### Backend Track

- [ ] 08.B1 Central spectroid signal: define the analysis input for central spectroid, note, or chord-reactive triggering.
- [ ] 08.B2 Chase layer spec: define a note or chord-reactive shader named `spectroid_chase` in `backend/shaders/`.
- [ ] 08.B3 Parcan anchor selection: use parcan fixture positions as chase origin anchors on the canvas.
- [ ] 08.B4 Chase path generation: generate outward line motion from parcan anchors toward the canvas.
- [ ] 08.B5 Moving head follow lines: define line-follow behavior that moving heads can track visually later.
- [ ] 08.B6 Parameter schema: define controls for trigger sensitivity, line length, spread, fade, and chase speed.
- [ ] 08.B7 Preset integration: make the shader usable from the preset and layer system.

### Frontend Track

- [ ] 08.F1 Shader metadata types: add frontend-readable types for the `spectroid_chase` shader and its parameter schema.
- [ ] 08.F2 Fixture-anchor readiness: make the UI able to consume parcan-anchor and moving-head-line controls later.
- [ ] 08.F3 Overlay compatibility: ensure fixture and POI overlays remain useful while previewing the chase shader.

### Validation Track

- [ ] 08.V1 Trigger response test: prove the shader reacts deterministically to the central spectroid or note/chord signal.
- [ ] 08.V2 Parcan anchor test: prove chase lines start from parcan positions.
- [ ] 08.V3 Line-follow test: prove outward line motion is stable and visually trackable for moving-head follow behavior.
- [ ] 08.V4 Snapshot test: add at least one visual fixture or snapshot test for the spectroid chase shader.

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

## Epic 10: Transition System

### Backend Track

- [ ] 10.B1 Transition model: define transition type, alignment target, duration, and params.
- [ ] 10.B2 Hard cut: implement hard cut transitions.
- [ ] 10.B3 Crossfade: implement crossfade transitions.
- [ ] 10.B4 Beat flash cut: implement beat flash cut transitions.
- [ ] 10.B5 Beat-aware alignment: allow transitions to snap to beat, bar, phrase, or section boundaries.
- [ ] 10.B6 Transition metadata: expose transition metadata in render artifacts.
- [ ] 10.B7 Transition debug info: expose preview or debug information in artifacts.

### Frontend Track

- [ ] 10.F1 Transition types: add frontend types for transition metadata.
- [ ] 10.F2 Transition preview readiness: make the UI able to consume transition metadata later.

### Validation Track

- [ ] 10.V1 Deterministic transition test: prove transition output is reproducible.
- [ ] 10.V2 Duration test: prove transition durations can be expressed and applied consistently.
- [ ] 10.V3 Alignment test: prove transitions honor beat, bar, phrase, or section alignment rules.

## Epic 11: Fixture Mapping And Export

### Backend Track

- [ ] 11.B1 Canonical pixel order: document and encode the canonical origin and row-major pixel order.
- [ ] 11.B2 Fixture reference schema: treat `data/fixtures/fixtures.json` as real fixture instances with fixture-type id and normalized canvas location.
- [ ] 11.B3 POI reference schema: treat `data/fixtures/pois.json` as normalized points of interest with optional per-fixture pan and tilt calibration targeting `ref_0_0_0`.
- [ ] 11.B4 Mapping config: define fixture or layout mapping inputs.
- [ ] 11.B5 Linear mapping: support linear pixel order.
- [ ] 11.B6 Serpentine mapping: support serpentine pixel order.
- [ ] 11.B7 Export manifest v1: export mapped frame metadata without changing the canonical render artifact.
- [ ] 11.B8 Gamma correction: add gamma correction to export.
- [ ] 11.B9 Brightness limiting: add brightness limiting to export.

### Frontend Track

- [ ] 11.F1 Export metadata types: add frontend types for export and mapping metadata.
- [ ] 11.F2 Export review readiness: make the UI able to inspect export metadata and mapping results later.
- [ ] 11.F3 Fixture and POI reference types: add frontend-readable types for fixture instances and POIs.

### Validation Track

- [ ] 11.V1 Orientation test pattern: add a test pattern that makes orientation obvious.
- [ ] 11.V2 Ordering test pattern: add a test pattern that makes pixel ordering obvious.
- [ ] 11.V3 Mapping validation: add validation checks for orientation, ordering, and layout mapping.

## Epic 12: Render Diagnostics

### Backend Track

- [ ] 12.B1 Diagnostics summary: compute brightness, average color, frame delta, blank-frame warnings, and render duration.
- [ ] 12.B2 Variety metrics: add beat-response and section-variation style signals that flag static or repetitive renders.
- [ ] 12.B3 Contact sheets: generate contact sheets for each render.
- [ ] 12.B4 Preview strip or GIF: generate a short preview strip or GIF for each render.

### Frontend Track

- [ ] 12.F1 Diagnostics types: add frontend types for diagnostics summaries and warnings.
- [ ] 12.F2 Diagnostics view: surface diagnostics summaries, warnings, and persistent artifact-status metadata in the console UI.
- [ ] 12.F3 Diagnostics asset view: surface contact sheets and preview assets in the UI.

### Validation Track

- [ ] 12.V1 Blank render test: catch obviously blank renders.
- [ ] 12.V2 Static render test: catch accidentally static renders.
- [ ] 12.V3 Regression change test: catch accidental visual output changes.
- [ ] 12.V4 Browser baseline suite: capture the named browser cases from `spec-browser-visual-regression.md` against the live Dockerized app.
- [ ] 12.V5 Overlay regression suite: compare fixture and POI overlay baselines separately from raw canvas baselines.
- [ ] 12.V6 Diagnostics asset regression suite: compare contact sheets, preview strips, and warning states in the browser UI.
- [ ] 12.V7 Review-console regression suite: compare approval, fullscreen, frame-inspector, timeline, and A/B compare states in the browser UI.
