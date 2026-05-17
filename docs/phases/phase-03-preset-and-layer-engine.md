# Phase 3: Preset And Layer Engine

## Goal

Move from hardcoded shader orchestration to a reusable low-res visual engine. Presets should compose layers, palettes, blend modes, masks, and modulators.

## Included Epics

- [Epic 06: Preset Schema](../epics/06-preset-schema.md)
- [Epic 04: Layer Library](../epics/04-layer-library.md)
- [Epic 05: Modulation System](../epics/05-modulation-system.md)
- [Epic 07: Raindrops Shader](../epics/07-raindrops-shader.md)
- [Epic 08: Spectroid Chase Shader](../epics/08-spectroid-chase-shader.md)
- [Epic 13: Ocean Waves Shader](../epics/13-ocean-waves-shader.md)

## Deliverables

- Preset files or structured preset definitions.
- Layer registry.
- Dedicated `backend/shaders/` source folder for backend shader and layer modules.
- Simple `bouncing_ball` test shader for first-pass renderer and preview verification.
- Palette system.
- Blend modes.
- POI-aware shader behaviors.
- Fixture-aware chase behaviors.
- Parcan-first ocean wave behavior.
- Stateful per-preset render context.
- Staged math execution contexts for preset init, per-frame, and bounded hot-path evaluation.
- Bounded shared state or register flow for presets and layers.
- Seeded randomness.

## Exit Criteria

- The current wave and pulse looks are represented as presets.
- The `bouncing_ball` test shader can render and preview a single deterministic bouncing point across the full canvas.
- A POI-driven raindrop look can be rendered without hardcoding a song-specific path.
- A note or chord-reactive chase look can start from parcan anchors and expand outward as moving-head-following lines.
- A deep-blue ocean-wave look can move left to right across the canvas with large swells and inner contrast that remain readable on parcans.
- Adding a new look places its backend shader implementation in `backend/shaders/` and does not require changing renderer control flow.
- Presets can express organic motion through deterministic staged math and bounded shared state instead of custom renderer wiring.
- Parameters can be introspected by the frontend.

