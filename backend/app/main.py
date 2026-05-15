"""
Main FastAPI Application

Epic 01: Render Contract - Backend implementation
"""

import logging
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


# Global state (in production, use a proper database)
_playback_state: Optional[PlaybackState] = None
_render_id_generator = RenderIdGenerator()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info("AI Light Show Backend starting up")
    yield
    logger.info("AI Light Show Backend shutting down")


# Create FastAPI app
app = FastAPI(
    title="AI Light Show Backend",
    description="Phase 1: Render Contract Implementation",
    version="0.1.0",
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


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"},
    )
