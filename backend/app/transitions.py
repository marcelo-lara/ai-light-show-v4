"""
Transition System

Epic 10: Transition System - Define and render scene transitions
"""

from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import numpy as np


class TransitionType(str, Enum):
    """Type of transition between scenes."""
    HARD_CUT = "hard_cut"
    CROSSFADE = "crossfade"
    BEAT_FLASH_CUT = "beat_flash_cut"


class AlignmentType(str, Enum):
    """Alignment for transition timing."""
    BEAT = "beat"
    BAR = "bar"
    PHRASE = "phrase"
    SECTION = "section"
    FRAME = "frame"


class Transition(BaseModel):
    """
    Epic 10.B1: Transition model defining type, alignment, duration, and params.
    
    A transition occurs between two scenes and can span multiple frames.
    """
    transition_id: str = Field(..., description="Unique transition identifier")
    from_scene_id: str = Field(..., description="Scene being transitioned from")
    to_scene_id: str = Field(..., description="Scene being transitioned to")
    
    # Type and timing
    type: TransitionType = Field(default=TransitionType.HARD_CUT)
    alignment: AlignmentType = Field(default=AlignmentType.BEAT)
    duration: float = Field(default=0.0, ge=0, description="Duration in seconds (0 = hard cut)")
    
    # Timing info
    start_time: float = Field(..., ge=0, description="Transition start time in seconds")
    end_time: Optional[float] = Field(None, ge=0, description="Transition end time (computed)")
    
    # Musical alignment (optional)
    start_beat: Optional[int] = Field(None)
    start_bar: Optional[int] = Field(None)
    start_phrase: Optional[int] = Field(None)
    start_section: Optional[int] = Field(None)
    
    # Transition-specific parameters
    params: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def compute_end_time(self) -> float:
        """Compute transition end time from start + duration."""
        return self.start_time + self.duration
    
    def get_transition_progress(self, current_time: float) -> float:
        """
        Get transition progress at a time.
        
        Args:
            current_time: Absolute time in seconds
            
        Returns:
            Progress 0.0-1.0, or -1 if not in transition window
        """
        if current_time < self.start_time:
            return -1
        
        if self.duration == 0:
            return 0 if current_time == self.start_time else -1
        
        end = self.end_time or self.compute_end_time()
        if current_time > end:
            return -1
        
        return (current_time - self.start_time) / self.duration


class HardCutTransition(Transition):
    """
    Epic 10.B2: Hard cut transition (instant scene switch).
    
    No intermediate frames, switches immediately.
    """
    type: TransitionType = Field(default=TransitionType.HARD_CUT)
    duration: float = Field(default=0.0)
    
    def render_transition_frame(
        self,
        frame_from: np.ndarray,
        frame_to: np.ndarray,
        progress: float,
    ) -> np.ndarray:
        """
        Render hard cut transition frame.
        
        Args:
            frame_from: Output frame from 'from' scene
            frame_to: Output frame from 'to' scene
            progress: Progress 0-1 (unused for hard cut)
            
        Returns:
            Transition frame (always frame_to)
        """
        return frame_to.copy()


class CrossfadeTransition(Transition):
    """
    Epic 10.B3: Crossfade transition (linear blend).
    
    Interpolates between old and new scenes over specified duration.
    """
    type: TransitionType = Field(default=TransitionType.CROSSFADE)
    duration: float = Field(default=1.0, ge=0.1, le=10.0)
    
    def render_transition_frame(
        self,
        frame_from: np.ndarray,
        frame_to: np.ndarray,
        progress: float,
    ) -> np.ndarray:
        """
        Render crossfade transition frame.
        
        Args:
            frame_from: Output frame from 'from' scene
            frame_to: Output frame from 'to' scene
            progress: Progress 0-1
            
        Returns:
            Blended transition frame
        """
        frame_from_f = frame_from.astype(np.float32) / 255.0
        frame_to_f = frame_to.astype(np.float32) / 255.0
        
        # Linear interpolation
        blended = frame_from_f * (1 - progress) + frame_to_f * progress
        
        # Clamp and convert back to uint8
        result = (np.clip(blended, 0, 1) * 255).astype(np.uint8)
        return result


class BeatFlashCutTransition(Transition):
    """
    Epic 10.B4: Beat flash cut transition.
    
    Full white flash on beat onset, then hard cut to new scene.
    Combines visual impact with scene change.
    """
    type: TransitionType = Field(default=TransitionType.BEAT_FLASH_CUT)
    duration: float = Field(default=0.1, ge=0.05, le=0.5)
    
    def render_transition_frame(
        self,
        frame_from: np.ndarray,
        frame_to: np.ndarray,
        progress: float,
    ) -> np.ndarray:
        """
        Render beat flash cut transition frame.
        
        First half: white flash (fade out)
        Second half: transition to new frame (fade in)
        
        Args:
            frame_from: Output frame from 'from' scene
            frame_to: Output frame from 'to' scene
            progress: Progress 0-1
            
        Returns:
            Flash + cut transition frame
        """
        if progress < 0.5:
            # Flash phase: fade from white to frame_to
            flash_progress = progress * 2  # 0-1 for first half
            
            # White frame
            white = np.ones_like(frame_from, dtype=np.float32) * 255
            frame_to_f = frame_to.astype(np.float32)
            
            # Fade from white to new frame
            blended = white * (1 - flash_progress) + frame_to_f * flash_progress
            result = blended.astype(np.uint8)
        else:
            # Cut phase: fully on new frame
            result = frame_to.copy()
        
        return result


class TransitionAligner:
    """
    Epic 10.B5, B5: Beat-aware alignment for transitions.
    
    Snaps transitions to beat, bar, phrase, or section boundaries.
    """
    
    @staticmethod
    def align_to_beat(
        transition_time: float,
        beat_times: List[float],
    ) -> float:
        """
        Align transition time to nearest beat.
        
        Args:
            transition_time: Requested time
            beat_times: List of beat times
            
        Returns:
            Aligned time to nearest beat
        """
        if not beat_times:
            return transition_time
        
        # Find nearest beat
        closest_beat = min(beat_times, key=lambda b: abs(b - transition_time))
        return closest_beat
    
    @staticmethod
    def align_to_bar(
        transition_time: float,
        beat_times: List[float],
        beats_per_bar: int = 4,
    ) -> float:
        """
        Align transition time to nearest bar boundary.
        
        Args:
            transition_time: Requested time
            beat_times: List of beat times
            beats_per_bar: Beats per bar (typically 4)
            
        Returns:
            Aligned time to nearest bar
        """
        if not beat_times or len(beat_times) < beats_per_bar:
            return transition_time
        
        # Get bar-aligned beat times
        bar_beat_times = [beat_times[i] for i in range(0, len(beat_times), beats_per_bar)]
        
        # Find nearest bar
        closest_bar = min(bar_beat_times, key=lambda b: abs(b - transition_time))
        return closest_bar
    
    @staticmethod
    def align_to_phrase(
        transition_time: float,
        phrase_boundaries: List[float],
    ) -> float:
        """
        Align transition time to nearest phrase boundary.
        
        Args:
            transition_time: Requested time
            phrase_boundaries: List of phrase start times
            
        Returns:
            Aligned time to nearest phrase
        """
        if not phrase_boundaries:
            return transition_time
        
        # Find nearest phrase boundary
        closest = min(phrase_boundaries, key=lambda p: abs(p - transition_time))
        return closest
    
    @staticmethod
    def align_to_section(
        transition_time: float,
        section_boundaries: List[float],
    ) -> float:
        """
        Align transition time to nearest section boundary.
        
        Args:
            transition_time: Requested time
            section_boundaries: List of section start times
            
        Returns:
            Aligned time to nearest section
        """
        if not section_boundaries:
            return transition_time
        
        # Find nearest section boundary
        closest = min(section_boundaries, key=lambda s: abs(s - transition_time))
        return closest


class TransitionDebugInfo(BaseModel):
    """
    Epic 10.B7: Debug information for transitions.
    
    Exposes timing, alignment decisions, and parameter values.
    """
    transition_id: str
    type: TransitionType
    start_time: float
    end_time: float
    duration: float
    progress_at_sample: Optional[float] = None
    alignment_info: Dict[str, Any] = Field(default_factory=dict)
    parameter_snapshot: Dict[str, Any] = Field(default_factory=dict)


def create_transition_debug_info(
    transition: Transition,
    current_frame_time: Optional[float] = None,
) -> TransitionDebugInfo:
    """
    Create debug information for a transition.
    
    Args:
        transition: Transition to debug
        current_frame_time: Current frame time (optional, for progress)
        
    Returns:
        TransitionDebugInfo with all details
    """
    progress = None
    if current_frame_time is not None:
        progress = transition.get_transition_progress(current_frame_time)
    
    alignment_info = {
        "alignment_type": transition.alignment.value,
        "beat": transition.start_beat,
        "bar": transition.start_bar,
        "phrase": transition.start_phrase,
        "section": transition.start_section,
    }
    
    return TransitionDebugInfo(
        transition_id=transition.transition_id,
        type=transition.type,
        start_time=transition.start_time,
        end_time=transition.end_time or transition.compute_end_time(),
        duration=transition.duration,
        progress_at_sample=progress,
        alignment_info=alignment_info,
        parameter_snapshot=transition.params,
    )
