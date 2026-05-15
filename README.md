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

## Phase 1: Render Contract ✅ COMPLETE

**Status:** Phase 1 is fully implemented and ready for development.

Phase 1 establishes the render contract and baseline infrastructure:

### Key Features
- ✅ **Versioned Schema**: `RenderArtifactMetadata` with complete metadata
- ✅ **Stable Render IDs**: Deterministic hash-based identifiers for reproducibility
- ✅ **Seed-based Rendering**: Explicit seed handling for deterministic outputs
- ✅ **Compatibility Validation**: Schema version checking and required field validation
- ✅ **Backend State Management**: Server-owned song and canvas state
- ✅ **Empty Canvas Support**: Songs load without existing renders
- ✅ **Chunked Binary Frames**: Progressive loading with 15KB chunks instead of monolithic files
- ✅ **Render Diagnostics**: Metrics for brightness, variety, static/blank frame detection
- ✅ **Type Safety**: Full TypeScript + Pydantic coverage

### Project Structure
```
backend/
  app/
    main.py              # FastAPI application
    models.py            # Render contract schemas
    render_contract.py   # Render ID & validation logic
    diagnostics.py       # Render diagnostics
    chunked_frames.py    # Binary frame I/O
  tests/
    test_render_contract.py
    test_diagnostics.py
    test_chunked_frames.py

frontend/
  src/
    api/backend.ts       # HTTP client
    types/renderContract.ts  # TypeScript interfaces
    store/playback.ts    # Zustand state
    components/          # React components
    App.tsx             # Main app
    main.tsx            # Entry point
  index.html
  vite.config.ts

docker-compose.yml
Dockerfile.backend
Dockerfile.frontend
```

### Quick Start

#### Prerequisites
- Docker and Docker Compose installed

#### Build and Run
```bash
# Build containers
docker compose build

# Start services (backend :3401, frontend :3400)
docker compose up -d

# View logs
docker compose logs -f
```

#### Test
```bash
# Run backend tests
docker compose run backend poetry run pytest tests/ -v

# Frontend type checking
docker compose run frontend npm run type-check
```

#### Access
- **Frontend UI**: http://localhost:3400
- **Backend API**: http://localhost:3401
- **API Documentation**: http://localhost:3401/docs

### API Endpoints (Phase 1)

**Playback State**
- `GET /api/playback/state` — Get backend-owned state
- `POST /api/songs/{song_id}/load` — Load song
- `POST /api/playback/play` — Start playback
- `POST /api/playback/stop` — Stop playback

**Render Contract**
- `POST /api/render/generate-id` — Generate stable render_id
- `POST /api/render/validate` — Validate artifact compatibility
- `GET /api/render/{render_id}/status` — Get render status

### Implementation Highlights

1. **Deterministic Rendering**
   - Same inputs (song, preset, seed, params) always produce identical render_id
   - Prevents accidental render duplication
   - Enables content addressing and caching

2. **Progressive Frame Loading**
   - Frames stored in ~1.5 MB chunks instead of one large file
   - Supports streaming playback without full memory load
   - `ChunkedFrameReader` for random access
   - `ChunkedFrameIterator` for streaming

3. **Render Diagnostics**
   - Automatic blank render detection
   - Static render flagging
   - Beat-response and variation scoring
   - Contact sheet and preview generation

4. **Type Safety**
   - Full Pydantic validation on backend
   - TypeScript interfaces on frontend
   - Automatic API documentation with Swagger

### Documentation

For detailed information:
- [Phase 1 Implementation](./PHASE_1_IMPLEMENTATION.md) — Complete implementation details
- [Phase Roadmap](./docs/phases/) — Development phases
- [Epics](./docs/epics/) — Epic specifications
- [Architecture & Specs](./docs/) — Technical specifications
- [Product Principles](./docs/product-principles.md) — Design philosophy

### Next: Phase 2 - Preview Console

Phase 2 will implement:
- Canvas rendering (100x50 grid visualization)
- Frame playback controls and scrubbing
- Fixture overlay visualization
- Preset parameter tuning UI
- Export workflow
