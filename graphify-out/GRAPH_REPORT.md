# Graph Report - .  (2026-05-17)

## Corpus Check
- Corpus is ~20,493 words - fits in a single context window. You may not need a graph.

## Summary
- 78 nodes · 139 edges · 15 communities (13 shown, 2 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 12 edges (avg confidence: 0.83)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Shader System Specs|Shader System Specs]]
- [[_COMMUNITY_Spatial Render Model|Spatial Render Model]]
- [[_COMMUNITY_Project Phases|Project Phases]]
- [[_COMMUNITY_Shared Preview Session|Shared Preview Session]]
- [[_COMMUNITY_Preset Ocean Waves|Preset Ocean Waves]]
- [[_COMMUNITY_Visual Regression|Visual Regression]]
- [[_COMMUNITY_Timeline Transitions|Timeline Transitions]]
- [[_COMMUNITY_Layer Raindrops|Layer Raindrops]]
- [[_COMMUNITY_Analysis Modulation|Analysis Modulation]]
- [[_COMMUNITY_Fixture Export|Fixture Export]]
- [[_COMMUNITY_Render Contract|Render Contract]]
- [[_COMMUNITY_Render Diagnostics|Render Diagnostics]]
- [[_COMMUNITY_Artifact Contract|Artifact Contract]]
- [[_COMMUNITY_Formula AST|Formula AST]]
- [[_COMMUNITY_Spectroid Chase|Spectroid Chase]]

## God Nodes (most connected - your core abstractions)
1. `Preview Console` - 8 edges
2. `Browser Visual Regression Suite` - 8 edges
3. `Phase 3: Preset And Layer Engine` - 8 edges
4. `AI Light Show Engine` - 7 edges
5. `Epic 06: Preset Schema` - 7 edges
6. `Shared Playback Transport` - 6 edges
7. `Ocean Waves Preset` - 6 edges
8. `Epic 04: Layer Library` - 6 edges
9. `Epic 13: Ocean Waves Shader` - 6 edges
10. `Epic 02: Preview Console` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Staged Evaluation` --uses--> `Musical Analysis IR`  [EXTRACTED]
  docs/spec-organic-visual-math.md → README.md
- `AI Light Show Engine` --reads_from--> `data/songs Directory`  [EXTRACTED]
  README.md → docs/spec-data-schemas.md
- `AI Light Show Engine` --reads_from--> `data/fixtures Directory`  [EXTRACTED]
  README.md → docs/spec-data-schemas.md
- `AI Light Show Engine` --writes_to--> `data/artifacts Directory`  [EXTRACTED]
  README.md → docs/spec-data-schemas.md
- `Shader-POI Interaction Model` --based_on--> `100x50 Virtual Canvas`  [EXTRACTED]
  docs/spec-shader-poi-interaction.md → README.md

## Hyperedges (group relationships)
- **Core Light Show Pipeline** — concept_musical_analysis_ir, concept_virtual_canvas_100x50, concept_fixture_mapping_dmx, concept_preview_console [EXTRACTED 1.00]
- **Preset Authoring Surface** — concept_staged_evaluation, concept_formula_ast, concept_preset_schema [EXTRACTED 1.00]
- **Browser Regression Named Baselines** — concept_browser_visual_regression, preset_bouncing_ball_reference_v1, preset_ocean_waves [EXTRACTED 1.00]
- **Phase 3 Preset Engine Stack** — phase_03, epic_04, epic_06 [EXTRACTED 1.00]
- **Shared Preview Session** — epic_01, epic_02, concept_shared_session [INFERRED 0.85]
- **Ocean Waves Stack** — epic_13, preset_ocean_waves, shader_ocean_waves [INFERRED 0.90]

## Communities (15 total, 2 thin omitted)

### Community 0 - "Shader System Specs"
Cohesion: 0.29
Nodes (13): data/fixtures Directory, Shader-POI Interaction Model, Epic 03: Analysis IR, Epic 04: Layer Library, Epic 05: Modulation System, Epic 06: Preset Schema, Epic 07: Raindrops Shader, Epic 08: Spectroid Chase Shader (+5 more)

### Community 1 - "Spatial Render Model"
Cohesion: 0.33
Nodes (9): AI Light Show Engine, data/songs Directory, Fixture Mapping and DMX Translation, Moving Head Pan/Tilt Translation, Musical Analysis IR, Parcan Sampling Intent, ref_0_0_0 Calibration Reference, 100x50 Virtual Canvas (+1 more)

### Community 2 - "Project Phases"
Cohesion: 0.33
Nodes (6): Phase 1: Baseline And Contracts, Phase 2: Musical Analysis IR, Phase 3: Preset And Layer Engine, Phase 4: Timeline And Direction, Phase 5: Production Console, Phase 6: Quality, Performance, And Packaging

### Community 3 - "Shared Preview Session"
Cohesion: 0.47
Nodes (6): Fixture and POI Overlay, Shared Playback Transport, Preview Console, Shared Backend Session State, Shared Backend Session, Epic 02: Preview Console

### Community 4 - "Preset Ocean Waves"
Cohesion: 0.47
Nodes (6): Preset Math Schema, Epic 06: Preset Schema, Epic 13: Ocean Waves Shader, Ocean Waves Preset, Undersea Pulse 01 Preset, Ocean Waves Shader

### Community 5 - "Visual Regression"
Cohesion: 0.6
Nodes (5): Browser Visual Regression Suite, data/artifacts Directory, Render Approval Workflow, Bouncing Ball Reference V1, Bouncing Ball Shader

### Community 6 - "Timeline Transitions"
Cohesion: 0.7
Nodes (5): Scene Timeline Metadata, Transition, Epic 09: Timeline Director, Epic 10: Transition System, Phase 4: Timeline And Direction

### Community 7 - "Layer Raindrops"
Cohesion: 0.5
Nodes (5): Layer Registry, Epic 04: Layer Library, Epic 07: Raindrops Shader, Phase 3: Preset And Layer Engine, Raindrops Shader

### Community 8 - "Analysis Modulation"
Cohesion: 0.7
Nodes (5): Analysis Intermediate Representation, Reusable Modulation Sources, Epic 03: Analysis IR, Epic 05: Modulation System, Phase 2: Musical Analysis IR

### Community 9 - "Fixture Export"
Cohesion: 0.67
Nodes (4): Export Manifest, Fixture Mapping, Epic 11: Fixture Mapping And Export, Phase 6: Quality, Performance, And Packaging

### Community 10 - "Render Contract"
Cohesion: 0.5
Nodes (4): Deterministic Rendering, Render Contract, Epic 01: Render Contract, Epic 02: Preview Console

### Community 11 - "Render Diagnostics"
Cohesion: 1.0
Nodes (3): Render Diagnostics, Epic 12: Render Diagnostics, Phase 5: Production Console

### Community 12 - "Artifact Contract"
Cohesion: 1.0
Nodes (3): Render Artifact, Epic 01: Render Contract, Phase 1: Baseline And Contracts

## Knowledge Gaps
- **6 isolated node(s):** `Deterministic Rendering`, `Phase 1: Baseline And Contracts`, `Phase 6: Quality, Performance, And Packaging`, `Fixture and POI Overlay`, `Raindrops Shader` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Browser Visual Regression Suite` connect `Visual Regression` to `Shader System Specs`, `Shared Preview Session`, `Preset Ocean Waves`?**
  _High betweenness centrality (0.238) - this node is a cross-community bridge._
- **Why does `Ocean Waves Preset` connect `Preset Ocean Waves` to `Analysis Modulation`, `Spatial Render Model`, `Visual Regression`?**
  _High betweenness centrality (0.205) - this node is a cross-community bridge._
- **Why does `Preview Console` connect `Shared Preview Session` to `Spatial Render Model`, `Render Contract`, `Render Diagnostics`, `Visual Regression`?**
  _High betweenness centrality (0.166) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Epic 06: Preset Schema` (e.g. with `Epic 04: Layer Library` and `Epic 05: Modulation System`) actually correct?**
  _`Epic 06: Preset Schema` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Deterministic Rendering`, `Phase 1: Baseline And Contracts`, `Phase 6: Quality, Performance, And Packaging` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._