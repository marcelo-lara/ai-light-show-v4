"""
Render Contract Models

Defines the data schema for rendered light shows following Phase 1 spec.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class RenderArtifactMetadata(BaseModel):
    """
    Epic 01.B1: Versioned canvas JSON schema with required metadata fields.
    
    Defines the stable metadata contract for all render artifacts.
    """
    schema_version: str = Field("1.0", description="Schema version for compatibility")
    render_id: str = Field(..., description="Stable render_id from reproducible inputs")
    preset_id: str = Field(..., description="ID of the preset used")
    preset_version: str = Field(..., description="Version of the preset")
    seed: int = Field(..., description="Random seed for deterministic rendering")
    song_id: str = Field(..., description="Source song ID")
    analysis_id: str = Field(..., description="Analysis (IR) ID")
    fps: int = Field(30, description="Frames per second")
    duration: float = Field(..., description="Duration in seconds")
    frame_count: int = Field(..., description="Total number of frames")
    params: Dict[str, Any] = Field(default_factory=dict, description="Render parameters")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None


class CanvasFrame(BaseModel):
    """
    Epic 01.B7: Individual canvas frame representation.
    
    A single 100x50 RGB frame with optional metadata.
    """
    frame_index: int
    data: List[int] = Field(..., description="RGB pixel data (100*50*3 = 15000 bytes)")


class ChunkedBinaryFrames(BaseModel):
    """
    Epic 01.B7: Chunked binary frames model for efficient storage.
    
    Splits large frame payloads into manageable chunks stored in data/artifacts/.
    Reduces memory pressure and enables progressive loading.
    """
    chunk_size: int = Field(default=100, description="Frames per chunk")
    total_chunks: int
    chunk_paths: List[str] = Field(..., description="Paths to chunk files in data/artifacts/")


class RenderArtifact(BaseModel):
    """
    Epic 01.B1-B3, B7: Complete render artifact contract.
    
    Encapsulates the render contract with metadata, frames, and diagnostics.
    """
    metadata: RenderArtifactMetadata
    frames: Optional[ChunkedBinaryFrames] = None
    checksum: Optional[str] = None


class CurrentCanvasState(BaseModel):
    """
    Epic 01.B5-B6: Backend-owned current canvas state.
    
    Represents the current loaded canvas for a song, or empty state.
    """
    song_id: str
    canvas_id: Optional[str] = None
    render_artifact: Optional[RenderArtifact] = None
    is_empty: bool = Field(default=False, description="True if no canvas loaded yet")


class CurrentSongState(BaseModel):
    """
    Epic 01.B5: Backend-owned current song state.
    
    Represents the currently loaded song in playback.
    """
    song_id: str
    title: Optional[str] = None
    duration: Optional[float] = None
    analysis_id: Optional[str] = None
    current_canvas: Optional[CurrentCanvasState] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PlaybackState(BaseModel):
    """
    Backend playback contract combining song and canvas state.
    """
    current_song: Optional[CurrentSongState] = None
    is_playing: bool = False
    playback_time: float = 0.0
