## Look
The visible result of a preset or scene. A look should be nameable and recognizable.

## POI (Point of Interest)
A defined physical and canvas coordinate in `data/fixtures/pois.json` that acts as a gravity well, collision target, or origin for shaders. It also serves as a calibration target for physical fixtures.

## Fixture Calibration (`ref_0_0_0`)
The physical origin point `[x:0, y:0, z:0]` used to translate 2D canvas coordinates into 3D vectors for moving heads. Moving heads store a baseline DMX Pan/Tilt value targeting this point.

## Transition
The visual bridge between two scenes. Transitions can crossfade, wipe, morph, hard cut, or beat-cut.

## Render Artifact
Any generated file output by the engine, stored in `data/artifacts/`. This includes analysis caches, chunked binary canvas frames, DMX export manifests, preview images, and reports.
