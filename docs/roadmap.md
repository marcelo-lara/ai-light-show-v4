# Roadmap

This roadmap is intentionally iterative. Each phase should leave the app more usable than before, even if later phases deepen the system.

## Phase Summary

1. **Phase 1: Baseline And Contracts**
   Stabilize the current `100x50` render contract, cache format, parameter behavior, and preview expectations.

2. **Phase 2: Musical Analysis IR**
   Expand audio analysis from raw features into show-ready musical signals.

3. **Phase 3: Preset And Layer Engine**
   Replace one-off shader wiring with composable presets, layers, modulators, palettes, and deterministic state.

4. **Phase 4: Timeline And Direction**
   Arrange visuals across song sections with transitions, cue points, intensity curves, and reviewable show structure.

5. **Phase 5: Production Console**
   Upgrade the frontend into a generation, tuning, inspection, and approval console.

6. **Phase 6: Quality, Performance, And Packaging**
   Add validation, visual regression checks, render diagnostics, cache management, and deployment-ready workflows.

## Epic Index

- [Epic 01: Render Contract](./epics/01-render-contract.md)
- [Epic 02: Preview Console](./epics/02-preview-console.md)
- [Epic 03: Analysis IR](./epics/03-analysis-ir.md)
- [Epic 04: Layer Library](./epics/04-layer-library.md)
- [Epic 05: Modulation System](./epics/05-modulation-system.md)
- [Epic 06: Preset Schema](./epics/06-preset-schema.md)
- [Epic 07: Raindrops Shader](./epics/07-raindrops-shader.md)
- [Epic 08: Spectroid Chase Shader](./epics/08-spectroid-chase-shader.md)
- [Epic 09: Timeline Director](./epics/09-timeline-director.md)
- [Epic 10: Transition System](./epics/10-transition-system.md)
- [Epic 11: Fixture Mapping And Export](./epics/11-fixture-mapping-and-export.md)
- [Epic 12: Render Diagnostics](./epics/12-render-diagnostics.md)

## Recommended Iteration Order

1. Lock the render contract and playback state contract.
2. Upgrade the frontend console for loading, rendering, overlays, inspection, and approval.
3. Expand analysis IR so layers can use musical timing and tonal signals.
4. Build the reusable layer library and core blend or transform behavior.
5. Add the modulation system so presets can drive layers without custom wiring.
6. Define the preset schema and parameter model.
7. Implement POI-native looks such as raindrop pulses and transit collisions.
8. Implement note or chord-reactive chase looks from parcan anchors into moving-head line motion.
9. Add timeline scenes and beat-synced transitions.
10. Add physical fixture mapping and export.
11. Add diagnostics and regression tests.
