"""
Render Job & Generation Status

Epic 02.B5: Render job status, progress, and failure details
Epic 02.B6: Analysis phase progress tracking
Epic 02.B7: Render progress cadence (every 200 frames)
Epic 02.B9: Progress phase payload with analysis vs render phases
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class RenderPhase(str, Enum):
    """Current phase of render job."""
    QUEUED = "queued"
    ANALYZING = "analyzing"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class RenderJobStatus(BaseModel):
    """
    Epic 02.B5, 02.B9: Render job status with progress tracking.
    
    Tracks current phase (analysis vs render) and numeric progress
    for progress bar display.
    """
    job_id: str
    phase: RenderPhase = RenderPhase.QUEUED
    status_text: str = "Queued"
    
    # Analysis phase progress (0-100)
    analysis_current: int = 0
    analysis_total: int = 0
    analysis_percent: float = 0.0
    
    # Render phase progress (0-100)
    render_current: int = 0
    render_total: int = 0
    render_percent: float = 0.0
    
    # Overall progress
    overall_percent: float = 0.0
    
    # Error details (if failed)
    error_message: Optional[str] = None
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if job is done (success or failure)."""
        return self.phase in [RenderPhase.COMPLETED, RenderPhase.FAILED]
    
    @property
    def is_failed(self) -> bool:
        """Check if job failed."""
        return self.phase == RenderPhase.FAILED


class AnalysisProgress(BaseModel):
    """
    Epic 02.B6: Analysis phase progress tracking.
    
    Reports on audio analysis progress before frame rendering begins.
    """
    stage: str  # "beat_detection", "frequency_analysis", "phrasing", etc.
    current: int
    total: int
    percent: float = 0.0
    status_text: str = ""


class RenderProgress(BaseModel):
    """
    Epic 02.B7: Render progress tracking with cadence every 200 frames.
    
    Current and total frame counts for progress bar updates.
    """
    current_frame: int
    total_frames: int
    percent: float = 0.0
    frames_per_second: float = 0.0
    estimated_seconds_remaining: float = 0.0


class CanvasNamingRequest(BaseModel):
    """
    Epic 02.B8: Canvas naming contract.
    
    User-provided canvas name to create exports as
    `{song_name}.{canvas_name}.json`
    """
    song_id: str
    canvas_name: str = Field(..., min_length=1, max_length=100)
    preset_ids: List[str] = Field(default_factory=list, description="Presets to render")
    seed: int = Field(default=12345, description="Random seed")
    params: Dict[str, Any] = Field(default_factory=dict, description="Render parameters")


class RenderRequest(BaseModel):
    """Request to start a render job for the current song."""
    canvas_name: str
    preset_ids: Optional[List[str]] = None
    seed: Optional[int] = None
    params: Optional[Dict[str, Any]] = None


class GenerationWorkflow(BaseModel):
    """
    Epic 02.B3: Render action contract.
    
    Complete workflow for creating or replacing current canvas.
    """
    job_id: str
    song_id: str
    canvas_name: str
    status: RenderJobStatus
    render_request: RenderRequest
