## Epic 02: Preview Console

### Backend Track

- [ ] 02.B1 Song load endpoint: add one backend action that sets the current song and returns the updated current song plus current canvas state.
- [ ] 02.B2 Missing canvas on load: make song-load succeed even when no show exists for that song.
- [ ] 02.B3 Render action contract: make `Render` create or replace the current canvas for the already loaded song.
- [ ] 02.B4 Metadata payload support: expose artifact metadata needed by the console without UI-only assumptions.
- [ ] 02.B5 Generation status payload: expose render job status, progress, and failure details through the API.
- [ ] 02.B6 Analysis phase progress: expose analysis-stage progress and status text before frame rendering begins.
- [ ] 02.B7 Render progress cadence: publish render progress with current and total frame counts at least every `200` frames.
- [ ] 02.B8 Canvas naming contract: accept a user-provided canvas name and persist exports as `{song_name}.{canvas_name}.json`.
- [ ] 02.B9 Progress phase payload wiring: extend job status so the API reports analysis vs render phase and enough numeric progress for the frontend progress bar to reflect the active phase.

### Frontend Track

- [ ] 02.F1 Console network spec: update the frontend to target port `3400` and the backend API on port `3401`.
- [ ] 02.F2 Server-owned song flow: request song changes from the backend instead of loading song files directly in the frontend.
- [ ] 02.F3 Song-loaded UI update: update the frontend when the backend reports a new current song and current canvas.
- [ ] 02.F4 Empty canvas state UI: allow a song to be loaded and preview-ready even when no show exists yet.
- [ ] 02.F5 Main tab: add a `Main` tab in the left column with only `show name` input and a `Render` button.
- [ ] 02.F6 Shader tabs: add one left-column tab per shader or layer property group.
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

### Validation Track

- [ ] 02.V1 Port configuration check: prove the frontend and backend run on the documented ports `3400` and `3401`.
- [ ] 02.V2 Schema error state test: prove incompatible artifacts show a clear UI state.
- [ ] 02.V3 Song load flow test: prove the frontend asks the backend to load a song and updates when the backend confirms the new current song.
- [ ] 02.V4 Missing canvas flow test: prove a song with no canvas still loads and only creates a show on `Render`.
- [ ] 02.V5 Left-tab layout test: prove the left column shows one `Main` tab and one tab per shader or layer group.
- [ ] 02.V6 Overlay load test: prove fixtures and POIs load from their JSON files and render as overlay references.
- [ ] 02.V7 Overlay alignment test: prove fixture and POI markers stay aligned to canvas coordinates.
- [ ] 02.V8 Review workflow test: prove a user can load a song, render a show, inspect it, and approve it from the UI.
- [ ] 02.V9 Full-width preview test: prove the canvas expands to the available width without distorting the render aspect ratio.
- [ ] 02.V10 Canvas name render test: prove the entered canvas name is sent to the backend and the resulting canvas file uses `{song_name}.{canvas_name}.json`.
- [ ] 02.V11 Progress phase test: prove the UI distinguishes analysis progress from render progress and updates render progress every `200` frames.
- [ ] 02.V12 Chunk compatibility flow test: prove the preview can still load and play a chunked v2 canvas artifact without changing current-canvas selection semantics.
- [ ] 02.V13 Preset tab selection flow test: prove the `Main` tab shows overwrite-default `show name` input plus preset checklist, and that selecting presets shows only those preset parameter tabs while unselected preset tabs remain hidden before render.

