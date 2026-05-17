# AI Light Show V3 Documentation

This folder is the working plan for turning the current prototype into a production-grade `100x50` pixel light-show visualizer.

The goal is not to clone BeatDrop as a full-screen MilkDrop renderer. BeatDrop is the reference for expressive visual systems: presets, audio response, shapes, waves, transitions, shader-like math, caching, and performance controls. Our product is different: it renders intentional low-resolution pixel output for a fixed light canvas.

## North Star

Create a precomputed visual engine that makes `100x50` pixels feel authored, musical, varied, and stage-ready.

That means:

- Every pixel has purpose.
- The low resolution is a creative constraint, not a limitation to hide.
- Shows are synchronized to song structure, not only raw beat hits.
- Looks are generated from reusable presets and layers, not one-off Python classes.
- The frontend is a production console for previewing, tuning, generating, and reviewing shows.
- Outputs are deterministic, cacheable, testable, and easy to compare.

## Documentation Map

- [Product Principles](./product-principles.md): what production-grade means for this project.
- [Roadmap](./roadmap.md): phases, epics, and iteration order.
- [Development Handoff Stories](./development-handoff-stories.md): concise implementation stories for delegating epic work.
- [Glossary](./glossary.md): shared terms for the engine and UI.
- [Organic Visual Math](./spec-organic-visual-math.md): BeatDrop or MilkDrop-inspired math patterns adapted to this project's deterministic low-res engine.
- [Preset Math Schema](./spec-preset-math-schema.md): concrete JSON shape for staged preset math, registers, and layer-local state.
- [Expression Authoring Model](./spec-expression-authoring-model.md): decision to store authored preset math as a structured formula AST instead of a free-form DSL.
- [Bouncing Ball Test Shader](./spec-bouncing-ball-test-shader.md): deterministic single-point shader spec for verifying backend canvas rendering and frontend preview playback.
- [Ocean Waves Shader](./spec-ocean-waves-shader.md): parcan-first deep-blue wave shader spec with large left-to-right swells and inner contrast.
- [Browser Visual Regression](./spec-browser-visual-regression.md): complete browser-driven visual regression case matrix for the live Dockerized preview console.
- [Phases](./phases): phase-level goals and exit criteria.
- [Epics](./epics): one file per epic story.

## Docs-Only Workflow Rule

When a task is explicitly marked as docs-only, keep the work strictly in documentation artifacts (plans, specs, stories, and checklists).

- Do not implement runtime features as part of the task.
- Do not run browser or end-to-end behavior tests for not-yet-implemented features.
- Capture intended behavior as explicit validation stories so implementation teams can verify later.
- Keep epic docs aligned with [Development Handoff Stories](./development-handoff-stories.md) as the source of truth for planning units.

## Epic Checklist

Checked items are done. The list is ordered by recommended implementation sequence.

- [ ] [Epic 01: Render Contract](./epics/01-render-contract.md)
- [ ] [Epic 02: Preview Console](./epics/02-preview-console.md)
- [ ] [Epic 03: Analysis IR](./epics/03-analysis-ir.md)
- [ ] [Epic 04: Layer Library](./epics/04-layer-library.md)
- [ ] [Epic 05: Modulation System](./epics/05-modulation-system.md)
- [ ] [Epic 06: Preset Schema](./epics/06-preset-schema.md)
- [ ] [Epic 07: Raindrops Shader](./epics/07-raindrops-shader.md)
- [ ] [Epic 08: Spectroid Chase Shader](./epics/08-spectroid-chase-shader.md)
- [ ] [Epic 09: Timeline Director](./epics/09-timeline-director.md)
- [ ] [Epic 10: Transition System](./epics/10-transition-system.md)
- [ ] [Epic 11: Fixture Mapping And Export](./epics/11-fixture-mapping-and-export.md)
- [ ] [Epic 12: Render Diagnostics](./epics/12-render-diagnostics.md)
- [ ] [Epic 13: Ocean Waves Shader](./epics/13-ocean-waves-shader.md)

## Current Baseline

The current codebase already has useful foundations:

- Full-track audio analysis with beat times, onset, and five normalized frequency bands.
- A structured separation between read-only song and room inputs (`data/songs/`, `data/fixtures/`) and generated outputs (`data/artifacts/`).
- A precomputed, chunked binary canvas cache.
- A browser player that synchronizes audio playback with cached frames.
- Two prototype shader classes: wave and radial pulse, which should be normalized into `backend/shaders/` as the production backend layout.
- A simple deterministic `bouncing_ball` shader should be used as the first rendering sanity-check look for backend and preview validation.
- A small tuning UI for generation parameters.

The main gap is architecture depth. Production quality should come from a richer engine model, better musical analysis, a preset/timeline system, stronger low-res rendering techniques, and a more complete preview workflow.
