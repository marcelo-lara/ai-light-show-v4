"""
Main FastAPI Application

Epic 01: Render Contract - Backend implementation
Epic 02: Preview Console - Backend song/render endpoints
"""

import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import (
    PlaybackState,
    CurrentSongState,
    CurrentCanvasState,
    RenderArtifactMetadata,
)
from .render_contract import (
    RenderIdGenerator,
    validate_artifact_compatibility,
    validate_seed,
)
from .render_job import (
    RenderJobStatus,
    RenderPhase,
    RenderRequest,
    GenerationWorkflow,
)
from .fixtures import FixtureManager
from .canvas import CanvasRenderer
from .preset import PresetRegistry
from .layers import LayerRegistry
from .modulation import ModulationSystem, ModulationContext
from .presets_builtin import get_builtin_presets


# Global state (in production, use a proper database)
_playback_state: Optional[PlaybackState] = None
_render_id_generator = RenderIdGenerator()
_render_jobs: dict = {}  # Job ID -> RenderJobStatus
_fixture_manager: Optional[FixtureManager] = None
_preset_registry: Optional[PresetRegistry] = None
_layer_registry: Optional[LayerRegistry] = None
_modulation_system: Optional[ModulationSystem] = None

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    global _fixture_manager, _preset_registry, _layer_registry, _modulation_system
    logger.info("AI Light Show Backend starting up")
    _fixture_manager = FixtureManager()
    
    # Phase 03: Initialize preset, layer, and modulation systems
    _preset_registry = PresetRegistry()
    _layer_registry = LayerRegistry()
    _modulation_system = ModulationSystem()
    
    # Load built-in presets
    builtin_presets = get_builtin_presets()
    for preset_key, preset in builtin_presets.items():
        try:
            _preset_registry.register_preset(preset, validate=True)
            logger.info(f"Loaded preset: {preset_key}")
        except Exception as e:
            logger.error(f"Failed to load preset {preset_key}: {str(e)}")
    
    yield
    logger.info("AI Light Show Backend shutting down")


# Create FastAPI app
app = FastAPI(
    title="AI Light Show Backend",
    description="Phase 1-3: Render Contract, Preview Console & Preset/Layer Engine",
    version="0.3.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3400", "localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


# Epic 01.B5: Backend playback state endpoints
@app.get("/api/playback/state", response_model=PlaybackState)
async def get_playback_state():
    """
    Epic 01.B5: Get current backend-owned playback state.
    
    Returns current_song and current_canvas state.
    """
    global _playback_state
    if _playback_state is None:
        _playback_state = PlaybackState()
    return _playback_state


@app.post("/api/songs/{song_id}/load")
async def load_song(song_id: str):
    """
    Load a song and return its state.
    
    Epic 01.B5: Backend owns song loading.
    Epic 01.B6: Song loads successfully even with no canvas yet.
    """
    global _playback_state
    
    try:
        # Epic 01.B6: Create empty canvas state for new song
        current_song = CurrentSongState(
            song_id=song_id,
            current_canvas=CurrentCanvasState(
                song_id=song_id,
                is_empty=True,
            ),
        )
        
        _playback_state = PlaybackState(current_song=current_song)
        
        logger.info(f"Loaded song: {song_id}")
        return {
            "status": "success",
            "song_id": song_id,
            "has_canvas": False,
            "state": _playback_state.model_dump(),
        }
    except Exception as e:
        logger.error(f"Failed to load song {song_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load song: {str(e)}",
        )


@app.post("/api/render/validate")
async def validate_render_artifact(artifact: dict):
    """
    Epic 01.B4: Validate render artifact compatibility.
    
    Checks for required fields and schema version compatibility.
    """
    is_valid, error_msg = validate_artifact_compatibility(artifact)
    
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": error_msg, "is_compatible": False},
        )
    
    # Epic 01.B3: Validate seed
    seed = artifact.get("seed")
    is_seed_valid, seed_error = validate_seed(seed)
    
    if not is_seed_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": seed_error, "is_compatible": False},
        )
    
    return {
        "is_compatible": True,
        "schema_version": artifact.get("schema_version"),
        "render_id": artifact.get("render_id"),
    }


@app.post("/api/render/generate-id")
async def generate_render_id(
    song_id: str,
    preset_id: str,
    seed: int,
    params: Optional[dict] = None,
):
    """
    Epic 01.B2: Generate stable render_id from reproducible inputs.
    
    The same inputs always produce the same render_id.
    """
    if params is None:
        params = {}
    
    # Validate seed
    is_valid, error_msg = validate_seed(seed)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
    
    render_id = _render_id_generator.get_or_generate_render_id(
        song_id, preset_id, seed, params
    )
    
    return {
        "render_id": render_id,
        "song_id": song_id,
        "preset_id": preset_id,
        "seed": seed,
    }


@app.get("/api/render/{render_id}/status")
async def get_render_status(render_id: str):
    """
    Get status and metadata of a render artifact.
    
    Epic 01: Returns metadata for UI display.
    """
    # This would load from data/artifacts/ in a real implementation
    return {
        "render_id": render_id,
        "status": "not_found",
        "error": "Render artifact not found",
    }


@app.post("/api/playback/play")
async def play():
    """Start playback of current song."""
    global _playback_state
    if _playback_state:
        _playback_state.is_playing = True
    return {"status": "playing"}


@app.post("/api/playback/stop")
async def stop():
    """Stop playback."""
    global _playback_state
    if _playback_state:
        _playback_state.is_playing = False
    return {"status": "stopped"}


# ============ Epic 02: Preview Console Endpoints ============

@app.get("/api/fixtures")
async def get_fixtures():
    """
    Epic 02.F7: Load fixture references.
    
    Get all fixtures for overlay on canvas.
    """
    if not _fixture_manager:
        return {"fixtures": []}
    
    return {
        "fixtures": _fixture_manager.get_fixtures(),
        "schema_version": "1.0",
    }


@app.get("/api/pois")
async def get_pois():
    """
    Epic 02.F8: Load POI references.
    
    Get all points of interest for overlay.
    """
    if not _fixture_manager:
        return {"pois": []}
    
    return {
        "pois": _fixture_manager.get_pois(),
        "schema_version": "1.0",
    }


@app.post("/api/render/start")
async def start_render(request: RenderRequest):
    """
    Epic 02.B3: Render action contract.
    
    Start a render job for the current song.
    Create or replace the current canvas.
    
    Args:
        request: Render parameters including canvas name and presets
    """
    global _playback_state, _render_jobs
    
    if not _playback_state or not _playback_state.current_song:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No song loaded. Load a song first.",
        )
    
    try:
        job_id = f"job_{str(uuid.uuid4())[:8]}"
        song_id = _playback_state.current_song.song_id
        
        # Determine seed
        seed = request.seed if request.seed is not None else 12345
        is_valid, error_msg = validate_seed(seed)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
        
        # Create render job
        job_status = RenderJobStatus(
            job_id=job_id,
            phase=RenderPhase.QUEUED,
            status_text="Queued for rendering",
        )
        _render_jobs[job_id] = job_status
        
        # Return workflow
        workflow = GenerationWorkflow(
            job_id=job_id,
            song_id=song_id,
            canvas_name=request.canvas_name,
            status=job_status,
            render_request=request,
        )
        
        logger.info(f"Started render job {job_id} for song {song_id}")
        return workflow.model_dump()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start render: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start render: {str(e)}",
        )


@app.get("/api/render/{job_id}/status")
async def get_render_status(job_id: str):
    """
    Epic 02.B5, 02.B9: Get render job status with progress.
    
    Returns current phase and numeric progress for UI progress bar.
    """
    if job_id not in _render_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Render job {job_id} not found",
        )
    
    status_obj = _render_jobs[job_id]
    return status_obj.model_dump()


@app.post("/api/render/{job_id}/progress")
async def update_render_progress(job_id: str, progress_data: dict):
    """
    Epic 02.B7: Update render progress (cadence every 200 frames).
    
    Called by render worker to report progress.
    """
    if job_id not in _render_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Render job {job_id} not found",
        )
    
    status_obj = _render_jobs[job_id]
    
    if "phase" in progress_data:
        status_obj.phase = RenderPhase(progress_data["phase"])
    
    if "render_current" in progress_data:
        status_obj.render_current = progress_data["render_current"]
        if status_obj.render_total > 0:
            status_obj.render_percent = (
                100.0 * status_obj.render_current / status_obj.render_total
            )
    
    if "render_total" in progress_data:
        status_obj.render_total = progress_data["render_total"]
    
    if "status_text" in progress_data:
        status_obj.status_text = progress_data["status_text"]
    
    return status_obj.model_dump()


@app.post("/api/render/{job_id}/complete")
async def complete_render(job_id: str, result_data: dict):
    """
    Epic 02.B3, 02.B8: Mark render job as complete.
    
    Save canvas artifact and update current canvas state.
    """
    if job_id not in _render_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Render job {job_id} not found",
        )
    
    global _playback_state
    
    try:
        status_obj = _render_jobs[job_id]
        status_obj.phase = RenderPhase.COMPLETED
        status_obj.status_text = "Render complete"
        
        # In a real implementation, would save the canvas artifact
        # For now, just update current canvas state
        if _playback_state and _playback_state.current_song:
            _playback_state.current_song.current_canvas = CurrentCanvasState(
                song_id=_playback_state.current_song.song_id,
                canvas_id=job_id,
                is_empty=False,
            )
        
        logger.info(f"Render job {job_id} completed")
        return {"status": "success", "job_status": status_obj.model_dump()}
        
    except Exception as e:
        logger.error(f"Failed to complete render: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete render: {str(e)}",
        )


@app.post("/api/render/{job_id}/fail")
async def fail_render(job_id: str, error_data: dict):
    """
    Mark render job as failed with error details.
    """
    if job_id not in _render_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Render job {job_id} not found",
        )
    
    status_obj = _render_jobs[job_id]
    status_obj.phase = RenderPhase.FAILED
    status_obj.status_text = "Render failed"
    status_obj.error_message = error_data.get("error_message", "Unknown error")
    
    logger.error(f"Render job {job_id} failed: {status_obj.error_message}")
    return status_obj.model_dump()


# ============ Phase 03: Preset and Layer Engine Endpoints ============

@app.get("/api/phase03/presets")
async def list_presets():
    """
    Epic 06.F1: List all available presets with metadata.
    
    Returns preset summaries for UI consumption.
    """
    if not _preset_registry:
        return {"presets": [], "count": 0}
    
    presets = _preset_registry.list_presets()
    return {
        "presets": [p.model_dump() for p in presets],
        "count": len(presets),
    }


@app.get("/api/phase03/presets/{preset_id}")
async def get_preset(preset_id: str, version: str = "latest"):
    """
    Get a specific preset by ID and version.
    
    Epic 06.F3: Preset loading readiness.
    """
    if not _preset_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset registry not initialized",
        )
    
    preset = _preset_registry.get_preset(preset_id, version)
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset {preset_id}:{version} not found",
        )
    
    return preset.model_dump()


@app.get("/api/phase03/layers")
async def list_layers():
    """
    Epic 04.F1-F2: List all available layers with schemas.
    
    Returns layer metadata for layer browser UI.
    """
    if not _layer_registry:
        return {"layers": [], "count": 0}
    
    layer_ids = _layer_registry.list_layers()
    layers = []
    
    for layer_id in layer_ids:
        layer = _layer_registry.get_layer(layer_id)
        if layer:
            schema = layer.get_parameter_schema()
            layers.append({
                "layer_id": layer.layer_id,
                "label": layer.label,
                "parameter_schema": schema,
                "blend_modes_supported": ["alpha", "max", "add", "multiply", "screen", "difference", "mask", "replace"],
            })
    
    return {
        "layers": layers,
        "count": len(layers),
    }


@app.get("/api/phase03/layers/{layer_id}")
async def get_layer_info(layer_id: str):
    """
    Get detailed information about a specific layer.
    
    Epic 04.F1: Layer metadata type for parameter introspection.
    """
    if not _layer_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layer registry not initialized",
        )
    
    layer = _layer_registry.get_layer(layer_id)
    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Layer {layer_id} not found",
        )
    
    schema = layer.get_parameter_schema()
    return {
        "layer_id": layer.layer_id,
        "label": layer.label,
        "parameter_schema": schema,
        "blend_modes_supported": list(BLEND_MODES.keys()),
    }


@app.get("/api/phase03/modulators")
async def list_modulators():
    """
    Epic 05.F2: List available modulator sources.
    
    Returns modulator information for modulation system inspection.
    """
    if not _modulation_system:
        return {"modulators": [], "count": 0}
    
    modulators = []
    for mod_id, mod in _modulation_system.modulators.items():
        modulators.append({
            "modulator_id": mod_id,
            "type": type(mod).__name__,
        })
    
    return {
        "modulators": modulators,
        "count": len(modulators),
    }


@app.post("/api/phase03/modulators/inspect")
async def inspect_modulators(context_data: dict):
    """
    Epic 05.B7, 05.F2: Get current modulator values for inspection.
    
    Returns debug output with live modulator values.
    """
    if not _modulation_system:
        return {"error": "Modulation system not initialized"}
    
    try:
        context = ModulationContext(
            frame_time=context_data.get("frame_time", 0.0),
            beat_progress=context_data.get("beat_progress", 0.0),
            bar_progress=context_data.get("bar_progress", 0.0),
            phrase_progress=context_data.get("phrase_progress", 0.0),
            onset_detected=context_data.get("onset_detected", False),
            fft_bands=context_data.get("fft_bands", []),
            seed=context_data.get("seed", 0),
        )
        
        debug_output = _modulation_system.get_debug_output(context)
        return debug_output
    except Exception as e:
        logger.error(f"Failed to inspect modulators: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to inspect modulators: {str(e)}",
        )


@app.post("/api/phase03/presets/validate")
async def validate_preset(preset_data: dict):
    """
    Epic 06.B6: Validate a preset before rendering.
    
    Returns validation errors if invalid, empty list if valid.
    """
    if not _preset_registry or not _layer_registry:
        return {"error": "Registry not initialized"}
    
    try:
        # Build PresetDefinition from data
        from .preset import PresetDefinition, PresetValidator
        
        preset = PresetDefinition(**preset_data)
        errors = PresetValidator.validate_preset(preset, _layer_registry.layers)
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
        }
    except Exception as e:
        logger.error(f"Failed to validate preset: {str(e)}")
        return {
            "is_valid": False,
            "errors": [str(e)],
        }


# Import BLEND_MODES for list endpoint
from .layers import BLEND_MODES


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"},
    )
