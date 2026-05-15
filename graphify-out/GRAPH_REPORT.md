# Graph Report - .  (2026-05-15)

## Corpus Check
- Corpus is ~10,530 words - fits in a single context window. You may not need a graph.

## Summary
- 103 nodes · 116 edges · 28 communities (9 shown, 19 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.83)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Core System Concepts|Core System Concepts]]
- [[_COMMUNITY_Visual Effects|Visual Effects]]
- [[_COMMUNITY_Feature Specifications|Feature Specifications]]
- [[_COMMUNITY_Development Phases|Development Phases]]
- [[_COMMUNITY_Data Structures|Data Structures]]
- [[_COMMUNITY_Music Choreography|Music Choreography]]
- [[_COMMUNITY_Layer Types|Layer Types]]
- [[_COMMUNITY_Processing Pipeline|Processing Pipeline]]
- [[_COMMUNITY_Domain 8|Domain 8]]
- [[_COMMUNITY_Domain 9|Domain 9]]
- [[_COMMUNITY_Domain 10|Domain 10]]
- [[_COMMUNITY_Domain 11|Domain 11]]
- [[_COMMUNITY_Domain 12|Domain 12]]
- [[_COMMUNITY_Domain 13|Domain 13]]
- [[_COMMUNITY_Domain 14|Domain 14]]
- [[_COMMUNITY_Domain 15|Domain 15]]
- [[_COMMUNITY_Domain 16|Domain 16]]
- [[_COMMUNITY_Domain 17|Domain 17]]
- [[_COMMUNITY_Domain 18|Domain 18]]
- [[_COMMUNITY_Domain 19|Domain 19]]
- [[_COMMUNITY_Domain 20|Domain 20]]
- [[_COMMUNITY_Domain 21|Domain 21]]
- [[_COMMUNITY_Domain 22|Domain 22]]
- [[_COMMUNITY_Domain 23|Domain 23]]
- [[_COMMUNITY_Domain 24|Domain 24]]
- [[_COMMUNITY_Domain 25|Domain 25]]
- [[_COMMUNITY_Domain 26|Domain 26]]
- [[_COMMUNITY_Domain 27|Domain 27]]

## God Nodes (most connected - your core abstractions)
1. `Modulation System` - 17 edges
2. `Layer Library` - 10 edges
3. `Analysis IR (Intermediate Representation)` - 9 edges
4. `Phase 3: Preset And Layer Engine` - 7 edges
5. `Epic 05: Modulation System` - 7 edges
6. `Transition System` - 6 edges
7. `Epic 01: Render Contract` - 6 edges
8. `Epic 04: Layer Library` - 6 edges
9. `Render Contract` - 5 edges
10. `Preset Schema` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Raindrops - Sash!` --thematic_match--> `Raindrops Shader`  [INFERRED]
  graphify-out/transcripts/Sash - Raindrops.txt → docs/epics/07-raindrops-shader.md
- `Onset` --component_of--> `Analysis IR (Intermediate Representation)`  [INFERRED]
  docs/epics/05-modulation-system.md → docs/epics/03-analysis-ir.md
- `Raindrops Shader` --based_on--> `Radial Pulse Layer`  [INFERRED]
  docs/epics/07-raindrops-shader.md → docs/epics/04-layer-library.md
- `ParCan L Instance` --instance_of--> `ParCan (RGB)`  [EXTRACTED]
  data/fixtures/fixtures.json → docs/epics/08-spectroid-chase-shader.md
- `ParCan R Instance` --instance_of--> `ParCan (RGB)`  [EXTRACTED]
  data/fixtures/fixtures.json → docs/epics/08-spectroid-chase-shader.md

## Communities (28 total, 19 thin omitted)

### Community 0 - "Core System Concepts"
Cohesion: 0.15
Nodes (13): Modulation System, Mapping Operation: Clamp, Mapping Operation: Curve, Mapping Operation: Invert, Mapping Operation: Lag, Mapping Operation: Quantize, Mapping Operation: Scale, Mapping Operation: Smooth (+5 more)

### Community 1 - "Visual Effects"
Cohesion: 0.18
Nodes (12): Canvas (100x50), Fixture, Point of Interest (POI), ParCan L Instance, ParCan R Instance, Moving Head, ParCan (RGB), Scanner Layer (+4 more)

### Community 2 - "Feature Specifications"
Cohesion: 0.27
Nodes (12): Fixture Mapping & Export, Preview Console, Render Contract, Render Diagnostics, Render Artifact, Epic 01: Render Contract, Epic 02: Preview Console, Epic 11: Fixture Mapping And Export (+4 more)

### Community 3 - "Development Phases"
Cohesion: 0.22
Nodes (10): Layer Library, Bars Layer, Beat Flash Layer, Gradient Field Layer, Radial Pulse Layer, Rings Layer, Solid Field Layer, Wave Layer (+2 more)

### Community 4 - "Data Structures"
Cohesion: 0.2
Nodes (10): Smoothed Band Envelope, Bar Phase, Beat Phase, Global Energy, Onset, Section Labels, Analysis IR (Intermediate Representation), Audio Modulator: Band Envelope (+2 more)

### Community 5 - "Music Choreography"
Cohesion: 0.28
Nodes (9): Preset Schema, Timeline Director, Transition System, Epic 09: Timeline Director, Epic 10: Transition System, Phase 4: Timeline And Direction, Beat Flash Cut Transition, Crossfade Transition (+1 more)

### Community 6 - "Layer Types"
Cohesion: 0.54
Nodes (8): Epic 03: Analysis IR, Epic 04: Layer Library, Epic 05: Modulation System, Epic 06: Preset Schema, Epic 07: Raindrops Shader, Epic 08: Spectroid Chase Shader, Phase 2: Musical Analysis IR, Phase 3: Preset And Layer Engine

### Community 7 - "Processing Pipeline"
Cohesion: 0.33
Nodes (6): Blend Mode, Modulator, Parameter, Preset, Scene, Transition

### Community 8 - "Domain 8"
Cohesion: 0.67
Nodes (3): Mini Beam Prism (L) Instance, Mini Beam Prism (R) Instance, Mini Beam Prism

## Knowledge Gaps
- **55 isolated node(s):** `Solid Field Layer`, `Gradient Field Layer`, `Bars Layer`, `Rings Layer`, `Beat Flash Layer` (+50 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Modulation System` connect `Core System Concepts` to `Data Structures`, `Music Choreography`, `Layer Types`?**
  _High betweenness centrality (0.193) - this node is a cross-community bridge._
- **Why does `Preset Schema` connect `Music Choreography` to `Core System Concepts`, `Feature Specifications`, `Development Phases`, `Layer Types`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `Layer Library` connect `Development Phases` to `Visual Effects`, `Music Choreography`, `Layer Types`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Epic 05: Modulation System` (e.g. with `Epic 06: Preset Schema` and `Epic 07: Raindrops Shader`) actually correct?**
  _`Epic 05: Modulation System` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Solid Field Layer`, `Gradient Field Layer`, `Bars Layer` to the rest of the system?**
  _55 weakly-connected nodes found - possible documentation gaps or missing edges._