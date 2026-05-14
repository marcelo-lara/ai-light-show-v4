# AI Light Show v4

The AI Light Show is a ML/AI tool designed to automatically generate organic, stage-ready DMX light shows from MP3 audio files.

Rather than relying on random noise or basic volume triggers, this engine extracts a deep musical understanding (Intermediate Representation) from the audio and uses it to drive deterministic, spatial math shaders on a `100x50` virtual canvas. This canvas is then physically mapped to actual DMX fixtures (Parcans and Moving Heads) using real-world coordinates and Points of Interest (POIs).

## How It Works (The 4-Step Pipeline)

1. **Audio Analysis (IR Extraction)**: Uses Essentia to extract beat grids, bar phases, musical phrasing, and 5-band FFT frequency envelopes from an MP3.
2. **Spatial Canvas Rendering**: Renders a `100x50` mathematical RGB canvas over time. Layers and shaders (like sine waves, raindrops, and spectroid chases) are anchored to physical fixture locations and POIs. The output is cached as chunked binary artifacts for high-performance playback.
3. **Fixture Mapping & DMX Translation**: 
    * **Static Wash (Parcans)**: Sample specific, fixed coordinates on the canvas.
    * **Moving Heads**: Calculate dynamic 3D vectors targeting the most intense or closest canvas coordinates relative to a physical calibration point (`ref_0_0_0`), translating 2D canvas coordinates into physical DMX Pan/Tilt instructions.
4. **Preview Console**: A Vite-based web frontend (Port `3400`) connected to a Python backend API (Port `3401`) to playback the MP3, visualize the `100x50` canvas with fixture overlays, tune preset parameters, and approve the final show before exporting to DMX.

## Data & Architecture

To maintain a clean separation of concerns, data is strictly separated:

* **`data/fixtures/`**: Read-only JSON schemas (`fixtures.json`, `pois.json`) defining the physical room layout, lighting hardware, and calibration points.
* **`data/artifacts/`**: Generated read/write engine outputs (audio IR caches, chunked binary canvas frames, DMX export manifests).
* **`data/songs/`**: The source MP3 audio files.

## Development Flow

- **Frontend Dev Server**: Port `3400`
- **Backend API Server**: Port `3401`
- **Docs-Only Tasks**: update plans/specs/stories only; do not treat unimplemented UI behavior as runtime-testable until implementation exists.

## Documentation

This project follows an iterative roadmap of Epics to ensure a production-grade result. 

For full details on the roadmap, epics, implementation handoff stories, and architectural specifications, please see the Documentation Hub.
