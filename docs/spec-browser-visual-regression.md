# Specification: Browser Visual Regression

## Objective

Define the full browser-driven visual regression suite for the review console using the live Dockerized app.

## Runtime Rules

- Run from the repo root.
- Always execute `docker compose down` then `docker compose up -d --build` before the suite.
- Validate against the live app on ports `3400` and `3401`.
- Do not mock song loading, render progress, overlays, diagnostics, or canvas frames.
- Use `data/songs/What a Feeling - Courtney Storm.mp3` as the default browser validation song.

## Deterministic Defaults

- Browser engine: Chromium.
- Browser locale: `en-US`.
- Browser timezone: `UTC`.
- Browser zoom: `100%`.
- Default regression seed: `424242`.
- Default canvas name: `vr_what_a_feeling`.
- Default song: `What a Feeling - Courtney Storm.mp3`.
- Default playback anchor for stable canvas captures: `00:30.000`.

## Capture Rules

- Freeze viewport size and browser zoom for every run.
- Capture the whole app shell and the canvas region separately.
- Use deterministic seeds and the same selected presets for baseline captures.
- Save baselines by feature and state, not by one giant end-to-end screenshot.
- Treat canvas diffs and overlay diffs as separate assertions.

## Viewport Profiles

| Profile | Size | Intended Cases |
|---|---:|---|
| `desktop` | `1440x900` | default shell, song flow, overlays, metadata, approval |
| `wide` | `1728x1080` | full-width preview, timeline, compare mode |
| `detail` | `1600x1000` | frame inspector, diagnostics panels, parameter groups |
| `fullscreen` | `1920x1080` | fullscreen preview and high-area canvas assertions |

## Capture Anchors

| Anchor | Meaning |
|---|---|
| `post_load` | app loaded, song list available, no render started |
| `post_song_select` | test song selected and current song state updated |
| `playing_00_30` | shared playback is actively running at `00:30.000` |
| `paused_00_30` | shared playback is paused at `00:30.000` |
| `stopped_00_00` | shared playback is stopped at `00:00.000` |
| `analysis_25` | analysis phase visibly in progress around one quarter of the bar |
| `render_50` | frame-render phase visibly in progress around mid-bar |
| `post_render` | render completed and current canvas available |
| `seek_00_30` | playback seeked to `00:30.000` after render completion |
| `seek_00_32` | playback seeked to `00:32.000` for short movement-step comparison captures |
| `seek_00_45` | playback seeked to `00:45.000` for later-scene captures |
| `bounce_ref_frame_08` | `bouncing_ball_reference_v1` paused on reference frame `8` at coordinate `(93, 43)` |
| `bounce_ref_frame_02` | `bouncing_ball_reference_v1` paused on reference frame `2` at coordinate `(99, 49)` |
| `bounce_edge_hit` | playback paused on a frame where the bouncing ball visibly touches and reflects from an edge |
| `approval_before` | rendered state before approval action |
| `approval_after` | same canvas after approval action |

## Baseline File Rules

- Baseline screenshots live under `data/artifacts/visual-regression/baselines/`.
- Current-run screenshots live under `data/artifacts/visual-regression/current/`.
- Diff screenshots live under `data/artifacts/visual-regression/diffs/`.
- Metadata lives under `data/artifacts/visual-regression/metadata/`.
- Screenshot filename format: `{case_id}.{viewport}.{surface}.png`.
- Metadata filename format: `{case_id}.{viewport}.{surface}.meta.json`.
- Diff filename format: `{case_id}.{viewport}.{surface}.diff.png`.

## Threshold Profiles

Comparison fails when either `max_diff_pixels` or `max_diff_ratio` is exceeded.

| Profile | max_diff_pixels | max_diff_ratio | Intended Use |
|---|---:|---:|---|
| `ui_strict` | `220` | `0.0015` | static shell and metadata UI |
| `canvas_strict` | `180` | `0.0020` | stable rendered canvas snapshots |
| `overlay_strict` | `60` | `0.0005` | fixture and POI marker alignment |
| `motion_relaxed` | `800` | `0.0060` | progress bars and transition-heavy states |
| `panel_strict` | `260` | `0.0018` | diagnostics, inspector, and parameter panels |
| `warning_strict` | `180` | `0.0012` | warnings and approval-state styling |

## Case Matrix

| Case | Surface | Viewport | Anchor | Baseline Filename | Threshold |
|---|---|---|---|---|---|
| `vr_app_shell_load` | `shell` | `desktop` | `post_load` | `vr_app_shell_load.desktop.shell.png` | `ui_strict` |
| `vr_song_selection_state` | `shell` | `desktop` | `post_song_select` | `vr_song_selection_state.desktop.shell.png` | `ui_strict` |
| `vr_song_loader_dropdown` | `shell` | `desktop` | `post_load` | `vr_song_loader_dropdown.desktop.shell.png` | `ui_strict` |
| `vr_render_progress_analysis` | `shell` | `desktop` | `analysis_25` | `vr_render_progress_analysis.desktop.shell.png` | `motion_relaxed` |
| `vr_render_progress_frames` | `shell` | `desktop` | `render_50` | `vr_render_progress_frames.desktop.shell.png` | `motion_relaxed` |
| `vr_canvas_baseline_playback` | `canvas` | `desktop` | `seek_00_30` | `vr_canvas_baseline_playback.desktop.canvas.png` | `canvas_strict` |
| `vr_transport_playing` | `shell` | `desktop` | `playing_00_30` | `vr_transport_playing.desktop.shell.png` | `ui_strict` |
| `vr_transport_paused` | `shell` | `desktop` | `paused_00_30` | `vr_transport_paused.desktop.shell.png` | `ui_strict` |
| `vr_transport_stopped` | `shell` | `desktop` | `stopped_00_00` | `vr_transport_stopped.desktop.shell.png` | `ui_strict` |
| `vr_fixture_overlay` | `canvas` | `desktop` | `seek_00_30` | `vr_fixture_overlay.desktop.canvas.png` | `overlay_strict` |
| `vr_poi_overlay` | `canvas` | `desktop` | `seek_00_30` | `vr_poi_overlay.desktop.canvas.png` | `overlay_strict` |
| `vr_overlay_alignment` | `canvas` | `wide` | `seek_00_30` | `vr_overlay_alignment.wide.canvas.png` | `overlay_strict` |
| `vr_metadata_panel` | `panel` | `desktop` | `post_render` | `vr_metadata_panel.desktop.panel.png` | `panel_strict` |
| `vr_frame_inspector` | `panel` | `detail` | `seek_00_30` | `vr_frame_inspector.detail.panel.png` | `panel_strict` |
| `vr_full_width_preview` | `canvas` | `wide` | `seek_00_30` | `vr_full_width_preview.wide.canvas.png` | `canvas_strict` |
| `vr_fullscreen_preview` | `canvas` | `fullscreen` | `seek_00_30` | `vr_fullscreen_preview.fullscreen.canvas.png` | `canvas_strict` |
| `vr_review_approval_state` | `shell` | `desktop` | `approval_before` | `vr_review_approval_state.desktop.shell.png` | `warning_strict` |
| `vr_review_approval_state_approved` | `shell` | `desktop` | `approval_after` | `vr_review_approval_state_approved.desktop.shell.png` | `warning_strict` |
| `vr_canvas_name_flow` | `shell` | `desktop` | `post_render` | `vr_canvas_name_flow.desktop.shell.png` | `ui_strict` |
| `vr_preset_checklist_visibility` | `shell` | `desktop` | `post_song_select` | `vr_preset_checklist_visibility.desktop.shell.png` | `ui_strict` |
| `vr_param_editor_groups` | `panel` | `detail` | `post_song_select` | `vr_param_editor_groups.detail.panel.png` | `panel_strict` |
| `vr_timeline_view` | `panel` | `wide` | `seek_00_45` | `vr_timeline_view.wide.panel.png` | `panel_strict` |
| `vr_ab_compare_layout` | `canvas` | `wide` | `seek_00_30` | `vr_ab_compare_layout.wide.canvas.png` | `canvas_strict` |
| `vr_shared_session_follower` | `shell` | `desktop` | `post_song_select` | `vr_shared_session_follower.desktop.shell.png` | `ui_strict` |
| `vr_bouncing_ball_canvas` | `canvas` | `desktop` | `bounce_ref_frame_08` | `vr_bouncing_ball_canvas.desktop.canvas.png` | `canvas_strict` |
| `vr_bouncing_ball_edge_bounce` | `canvas` | `desktop` | `bounce_ref_frame_02` | `vr_bouncing_ball_edge_bounce.desktop.canvas.png` | `canvas_strict` |
| `vr_ocean_waves_parcan_canvas` | `canvas` | `desktop` | `seek_00_30` | `vr_ocean_waves_parcan_canvas.desktop.canvas.png` | `canvas_strict` |
| `vr_ocean_waves_direction_step` | `canvas` | `desktop` | `seek_00_32` | `vr_ocean_waves_direction_step.desktop.canvas.png` | `motion_relaxed` |
| `vr_ocean_waves_inner_contrast` | `canvas` | `desktop` | `seek_00_30` | `vr_ocean_waves_inner_contrast.desktop.canvas.png` | `canvas_strict` |
| `vr_ocean_waves_preset_canvas` | `canvas` | `desktop` | `seek_00_30` | `vr_ocean_waves_preset_canvas.desktop.canvas.png` | `canvas_strict` |
| `vr_undersea_pulse_baseline` | `canvas` | `desktop` | `seek_00_30` | `vr_undersea_pulse_baseline.desktop.canvas.png` | `canvas_strict` |
| `vr_raindrops_poi_behavior` | `canvas` | `desktop` | `seek_00_30` | `vr_raindrops_poi_behavior.desktop.canvas.png` | `canvas_strict` |
| `vr_spectroid_chase_fixture_behavior` | `canvas` | `desktop` | `seek_00_30` | `vr_spectroid_chase_fixture_behavior.desktop.canvas.png` | `canvas_strict` |
| `vr_transition_crossfade` | `canvas` | `desktop` | `seek_00_45` | `vr_transition_crossfade.desktop.canvas.png` | `motion_relaxed` |
| `vr_transition_flash_cut` | `canvas` | `desktop` | `seek_00_45` | `vr_transition_flash_cut.desktop.canvas.png` | `motion_relaxed` |
| `vr_contact_sheet_panel` | `panel` | `detail` | `post_render` | `vr_contact_sheet_panel.detail.panel.png` | `panel_strict` |
| `vr_preview_strip_asset` | `panel` | `detail` | `post_render` | `vr_preview_strip_asset.detail.panel.png` | `panel_strict` |
| `vr_blank_render_warning` | `panel` | `detail` | `post_render` | `vr_blank_render_warning.detail.panel.png` | `warning_strict` |
| `vr_static_render_warning` | `panel` | `detail` | `post_render` | `vr_static_render_warning.detail.panel.png` | `warning_strict` |
| `vr_visual_regression_warning` | `panel` | `detail` | `post_render` | `vr_visual_regression_warning.detail.panel.png` | `warning_strict` |

## Preset And State Defaults

| Case Group | Preset Selection | Overlay State | Notes |
|---|---|---|---|
| shell and flow cases | default checked presets for the active story | overlays off unless the case names them | keep focus on layout stability |
| transport cases | same render as `vr_canvas_baseline_playback` | overlays off | capture playing, paused, and stopped button states separately |
| bouncing-ball cases | `bouncing_ball` only | overlays off | verify one-pixel motion, edge bounce, and preview crispness |
| ocean-wave cases | `ocean_waves` only | overlays off unless parcan sampling is being reviewed | verify large left-to-right swells and internal contrast survive low resolution |
| overlay cases | same canvas as `vr_canvas_baseline_playback` | overlays on | compare against raw canvas separately |
| raindrops case | `raindrops` only | overlays on | POI markers must remain visible |
| spectroid case | `spectroid_chase` only | overlays on | parcan anchors must remain readable |
| transition cases | timeline-enabled render with transition metadata | overlays off | capture after seeking to `00:45.000` |
| diagnostics cases | most recent completed render | overlays off | panel capture only |

## Bouncing Ball Reference Baseline

The `bouncing_ball` browser baselines must use preset `bouncing_ball_reference_v1` from `spec-bouncing-ball-test-shader.md`.

| Case | Expected Reference Frame | Expected Coordinate | Extra Assertion |
|---|---:|---|---|
| `vr_bouncing_ball_canvas` | `8` | `(93, 43)` | exactly one lit pixel on black background |
| `vr_bouncing_ball_edge_bounce` | `2` | `(99, 49)` | metadata must also record next reference frame `3` at `(98, 48)` |

The browser screenshot is not sufficient by itself for this shader. Each run should also record the decoded lit-pixel coordinate in metadata so the comparison can fail on path errors even when the point remains visually small.

## Core Cases

1. `vr_app_shell_load`
   Load the app after Docker startup and verify the main shell, tabs, and empty-state layout render without console-breaking errors.
2. `vr_song_selection_state`
   Load `What a Feeling - Courtney Storm.mp3` and verify the selected song name, current-song state, and initial current-canvas state.
3. `vr_song_loader_dropdown`
    Verify the song loader is a dropdown populated from the backend-visible contents of `data/songs/`.
4. `vr_render_progress_analysis`
   Trigger `Render` and capture the analysis-phase progress UI before frame rendering begins.
5. `vr_render_progress_frames`
   Continue the same render and capture the render-progress UI while frame counts advance.
6. `vr_canvas_baseline_playback`
   Capture the resulting rendered canvas in normal review mode with the default selected preset set.
7. `vr_transport_playing`
    Verify the `Play` button puts the shared session into a running playback state and the UI reflects active transport.
8. `vr_transport_paused`
    Verify the `Pause` button freezes playback at the current shared time and the UI reflects paused transport.
9. `vr_transport_stopped`
    Verify the `Stop` button returns playback to `00:00.000` and the UI reflects stopped transport.
10. `vr_fixture_overlay`
   Verify fixture references load from `data/fixtures/fixtures.json` and render in the correct canvas positions.
11. `vr_poi_overlay`
   Verify POI references load from `data/fixtures/pois.json` and render in the correct canvas positions.
12. `vr_overlay_alignment`
   Capture the canvas with overlays enabled and verify markers remain aligned while the canvas scales to available width.
13. `vr_metadata_panel`
   Verify schema version, render id, preset id, seed, and compatibility state render in the metadata panel.
14. `vr_frame_inspector`
    Open the frame inspector and verify coordinate and RGB readout overlays remain legible and correctly placed.

## Advanced Review Cases

15. `vr_full_width_preview`
    Verify the preview fills the available content width without aspect-ratio distortion.
16. `vr_fullscreen_preview`
    Verify fullscreen preview preserves the `100x50` pixel character and returns cleanly to the console layout.
17. `vr_review_approval_state`
    Capture the UI before and after approval so status styling and action affordances remain stable.
18. `vr_canvas_name_flow`
    Enter a canvas name, render, and verify the header and saved-current-canvas presentation use the chosen name.
19. `vr_preset_checklist_visibility`
    Verify unchecked presets stay hidden and checked presets expose only their matching parameter tabs.
20. `vr_param_editor_groups`
    Verify schema-driven parameter groups render in the expected tab and section order.
21. `vr_timeline_view`
    Verify scene and transition metadata render in the timeline area without overlap or clipping.
22. `vr_ab_compare_layout`
    Verify side-by-side compare mode preserves overlay legibility and consistent canvas scaling.
23. `vr_shared_session_follower`
    Verify a follower client updates to the same song, canvas, and transport state after another client changes the shared session.
24. `vr_bouncing_ball_canvas`
    Verify the `bouncing_ball` test shader renders as a single moving point and remains crisp in the frontend preview.
25. `vr_bouncing_ball_edge_bounce`
    Verify the same test shader visibly touches a canvas boundary and reflects in the expected direction.
26. `vr_ocean_waves_parcan_canvas`
    Verify the `ocean_waves` look reads as large deep-blue left-to-right swells with visible inner contrast when previewed as a parcan-first canvas.
27. `vr_ocean_waves_direction_step`
    Verify the dominant swell body shifts rightward between fixed playback anchors instead of drifting left or staying static.
28. `vr_ocean_waves_inner_contrast`
    Verify each large swell contains readable interior light or dark contrast instead of a flat color fill.

## Visual Output Cases

29. `vr_ocean_waves_preset_canvas`
    Capture the `ocean_waves` preset and verify large left-to-right swells, parcan-first readability, and stable deep-blue contrast.
30. `vr_undersea_pulse_baseline`
    Capture `undersea_pulse_01` and compare it against the baseline parity reference.
31. `vr_raindrops_poi_behavior`
    Capture `raindrops` with overlays enabled and verify visible POI-anchored pulse origins and collisions.
32. `vr_spectroid_chase_fixture_behavior`
    Capture `spectroid_chase` with overlays enabled and verify parcan-anchor readability and chase direction.
33. `vr_transition_crossfade`
    Capture one crossfade transition state and verify two-scene blend readability.
34. `vr_transition_flash_cut`
    Capture one beat-flash cut state and verify the transition remains intentional rather than clipped or blank.

## Diagnostics Cases

35. `vr_contact_sheet_panel`
    Verify diagnostics contact sheets render in the console and visually match the current render metadata.
36. `vr_preview_strip_asset`
    Verify preview strip or GIF assets render in the diagnostics area without distortion.
37. `vr_blank_render_warning`
    Verify blank-render warnings are visually obvious and do not break the rest of the review layout.
38. `vr_static_render_warning`
    Verify static-render warnings are visually obvious and can coexist with preview assets.
39. `vr_visual_regression_warning`
    Verify a regression-warning state can surface diff severity, changed asset references, and review actions.

## Failure Artifacts

- Save the actual screenshot, baseline screenshot, diff screenshot, and a small metadata JSON per case.
- Include current song, preset ids, seed, viewport, and current canvas name in failure metadata.
- Store generated artifacts under `data/artifacts/visual-regression/`, not under `data/songs/`.
- Include case id, surface, anchor, threshold profile, diff counts, and app commit id in every metadata JSON.

## Coverage Rule

The suite is complete only when every browser-visible feature in Epics `01`, `02`, `06`, `07`, `08`, `09`, `10`, `11`, and `12` maps to at least one named visual regression case in this document.