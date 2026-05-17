"""
Timeline and Scene Management

Epic 09: Timeline Director - Auto-generate and manage scene timelines
"""

from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json
from pydantic import BaseModel, Field


class AlignmentType(str, Enum):
    """Type of musical alignment for scene boundaries."""
    BEAT = "beat"
    BAR = "bar"
    PHRASE = "phrase"
    SECTION = "section"
    FRAME = "frame"  # Arbitrary frame boundary


class InterpolationType(str, Enum):
    """Interpolation method for automation curves."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    STEP = "step"


class ControlPoint(BaseModel):
    """Single control point in an automation curve."""
    time: float = Field(..., ge=0, description="Time in seconds from scene start")
    value: float = Field(..., ge=0, le=1, description="Normalized value 0-1")


class AutomationCurve(BaseModel):
    """
    Automation curve for intensity or parameter values.
    
    Maps time (relative to scene start) to normalized values (0-1).
    """
    name: str = Field(..., description="Name of automated parameter or 'intensity'")
    interpolation: InterpolationType = Field(
        default=InterpolationType.LINEAR,
        description="Interpolation method between control points"
    )
    control_points: List[ControlPoint] = Field(
        default_factory=list,
        description="Control points defining the curve"
    )
    
    def evaluate(self, time: float) -> float:
        """
        Evaluate automation curve at given time.
        
        Args:
            time: Time in seconds from scene start
            
        Returns:
            Normalized value 0-1
        """
        if not self.control_points:
            return 1.0
        
        # Handle before first point
        if time <= self.control_points[0].time:
            return self.control_points[0].value
        
        # Handle after last point
        if time >= self.control_points[-1].time:
            return self.control_points[-1].value
        
        # Find surrounding points
        for i in range(len(self.control_points) - 1):
            p0 = self.control_points[i]
            p1 = self.control_points[i + 1]
            
            if p0.time <= time <= p1.time:
                if p1.time == p0.time:
                    return p0.value
                
                # Normalize time to 0-1 between points
                t = (time - p0.time) / (p1.time - p0.time)
                
                # Apply interpolation
                if self.interpolation == InterpolationType.LINEAR:
                    t_interp = t
                elif self.interpolation == InterpolationType.EASE_IN:
                    t_interp = t * t
                elif self.interpolation == InterpolationType.EASE_OUT:
                    t_interp = t * (2 - t)
                elif self.interpolation == InterpolationType.EASE_IN_OUT:
                    t_interp = t * t * (3 - 2 * t)
                elif self.interpolation == InterpolationType.STEP:
                    t_interp = 0 if t < 0.5 else 1
                else:
                    t_interp = t
                
                # Linear interpolation
                return p0.value + (p1.value - p0.value) * t_interp
        
        return 1.0


@dataclass
class SceneMetadata:
    """Metadata for a scene."""
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_edited_at: datetime = field(default_factory=datetime.utcnow)


class Scene(BaseModel):
    """
    Scene: A time slice of the show using a specific preset and parameters.
    
    Epic 09.B1: Scene model defining preset, timing, automation, and metadata.
    """
    scene_id: str = Field(..., description="Unique scene identifier")
    start_time: float = Field(..., ge=0, description="Start time in seconds")
    end_time: float = Field(..., gt=0, description="End time in seconds")
    
    # Musical alignment (optional)
    start_beat: Optional[int] = Field(None, description="Beat index of start")
    start_bar: Optional[int] = Field(None, description="Bar index of start")
    start_phrase: Optional[int] = Field(None, description="Phrase index of start")
    start_section: Optional[int] = Field(None, description="Section index of start")
    
    # Preset and rendering
    preset_id: str = Field(..., description="ID of preset to use")
    seed: int = Field(default=0, description="Random seed for determinism")
    params: Dict[str, Any] = Field(default_factory=dict, description="Preset parameter overrides")
    
    # Automation
    intensity: float = Field(default=1.0, ge=0, le=1, description="Base intensity 0-1")
    intensity_automation: Optional[AutomationCurve] = Field(
        None, description="Optional intensity automation curve"
    )
    param_automation: Dict[str, AutomationCurve] = Field(
        default_factory=dict, description="Per-parameter automation curves"
    )
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Tags, notes, author")
    
    # Source tracking
    is_auto_generated: bool = Field(default=True, description="True if auto-generated")
    is_manual_override: bool = Field(default=False, description="True if manual override")
    
    def get_intensity_at_time(self, time: float) -> float:
        """
        Get effective intensity at a time within this scene.
        
        Args:
            time: Absolute time in seconds (scene will normalize to local time)
            
        Returns:
            Effective intensity 0-1
        """
        local_time = time - self.start_time
        
        if local_time < 0 or local_time > (self.end_time - self.start_time):
            return 0.0
        
        if self.intensity_automation:
            automation_value = self.intensity_automation.evaluate(local_time)
            return self.intensity * automation_value
        
        return self.intensity
    
    def get_param_value_at_time(self, param_name: str, default: Any = None) -> Any:
        """
        Get parameter value at current time (for diagnostics/preview).
        
        Args:
            param_name: Parameter name to query
            default: Default value if not found
            
        Returns:
            Parameter value or default
        """
        if param_name in self.params:
            return self.params[param_name]
        return default


class SceneTimeline(BaseModel):
    """
    Timeline: Collection of scenes and transitions for a song.
    
    Epic 09.B4: Manages auto-generated and manually-overridden scenes.
    """
    timeline_id: str = Field(..., description="Unique timeline identifier")
    song_id: str = Field(..., description="Source song ID")
    duration: float = Field(..., ge=0, description="Total song duration in seconds")
    
    scenes: List[Scene] = Field(default_factory=list, description="List of scenes in order")
    
    # Metadata
    auto_generated: bool = Field(default=True, description="True if timeline was auto-generated")
    generation_method: Optional[str] = Field(
        None, description="Method used for auto-generation: sections, phrases, beats"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_scene_at_time(self, time: float) -> Optional[Scene]:
        """
        Get the active scene at a given time.
        
        Args:
            time: Absolute time in seconds
            
        Returns:
            Scene at that time, or None if outside timeline
        """
        for scene in self.scenes:
            if scene.start_time <= time < scene.end_time:
                return scene
        return None
    
    def get_scenes_in_range(self, start_time: float, end_time: float) -> List[Scene]:
        """
        Get all scenes that overlap with a time range.
        
        Args:
            start_time: Range start in seconds
            end_time: Range end in seconds
            
        Returns:
            List of overlapping scenes
        """
        result = []
        for scene in self.scenes:
            if scene.end_time > start_time and scene.start_time < end_time:
                result.append(scene)
        return result
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate timeline consistency.
        
        Returns:
            (is_valid, list of error messages)
        """
        errors = []
        
        if not self.scenes:
            errors.append("Timeline has no scenes")
            return False, errors
        
        # Check chronological order
        prev_end = 0
        for i, scene in enumerate(self.scenes):
            if scene.start_time < prev_end:
                errors.append(f"Scene {i} starts before previous scene ends")
            if scene.end_time <= scene.start_time:
                errors.append(f"Scene {i} has end_time <= start_time")
            prev_end = scene.end_time
        
        # Check coverage (optional, but good practice)
        # Allow small gaps or overlaps for transitions
        
        return len(errors) == 0, errors


class TimelineGenerator:
    """
    Auto-generate timelines from song analysis data (IR).
    
    Epic 09.B2, B3: Generates first-pass timelines from sections/phrases/beats.
    """
    
    def __init__(self, available_presets: Optional[List[str]] = None):
        """
        Initialize generator.
        
        Args:
            available_presets: List of preset IDs to cycle through (or None for default)
        """
        self.available_presets = available_presets or ["undersea_pulse_01", "undersea_waves"]
        self.preset_idx = 0
    
    def generate_from_sections(
        self,
        song_id: str,
        duration: float,
        sections: List[Dict[str, Any]],
        base_seed: int = 0,
    ) -> SceneTimeline:
        """
        Epic 09.B2: Generate timeline from detected sections.
        
        One scene per section, cycling through available presets.
        
        Args:
            song_id: Source song ID
            duration: Song duration in seconds
            sections: List of section dicts with 'start', 'end', 'label' fields
            base_seed: Base seed for deterministic randomness
            
        Returns:
            Auto-generated SceneTimeline
        """
        scenes = []
        
        for i, section in enumerate(sections):
            start_time = section.get("start", 0)
            end_time = section.get("end", duration)
            label = section.get("label", f"Section {i}")
            
            # Cycle through presets
            preset_id = self.available_presets[i % len(self.available_presets)]
            
            # Deterministic seed
            seed = base_seed ^ (i * 31)  # XOR for variation
            
            scene = Scene(
                scene_id=f"{song_id}_scene_{i}",
                start_time=start_time,
                end_time=end_time,
                start_section=i,
                preset_id=preset_id,
                seed=seed,
                params={},
                intensity=1.0,
                metadata={
                    "section_label": label,
                    "section_index": i,
                },
                is_auto_generated=True,
            )
            scenes.append(scene)
        
        timeline = SceneTimeline(
            timeline_id=f"{song_id}_timeline_sections",
            song_id=song_id,
            duration=duration,
            scenes=scenes,
            auto_generated=True,
            generation_method="sections",
        )
        
        return timeline
    
    def generate_from_phrases(
        self,
        song_id: str,
        duration: float,
        phrases: List[Dict[str, Any]],
        base_seed: int = 0,
    ) -> SceneTimeline:
        """
        Epic 09.B3: Generate timeline from detected phrases.
        
        One scene per phrase, cycling through available presets.
        
        Args:
            song_id: Source song ID
            duration: Song duration in seconds
            phrases: List of phrase dicts with 'start', 'end' fields
            base_seed: Base seed for deterministic randomness
            
        Returns:
            Auto-generated SceneTimeline
        """
        scenes = []
        
        for i, phrase in enumerate(phrases):
            start_time = phrase.get("start", 0)
            end_time = phrase.get("end", duration)
            
            # Cycle through presets
            preset_id = self.available_presets[i % len(self.available_presets)]
            
            # Deterministic seed
            seed = base_seed ^ (i * 47)
            
            scene = Scene(
                scene_id=f"{song_id}_scene_{i}",
                start_time=start_time,
                end_time=end_time,
                start_phrase=i,
                preset_id=preset_id,
                seed=seed,
                params={},
                intensity=1.0,
                metadata={"phrase_index": i},
                is_auto_generated=True,
            )
            scenes.append(scene)
        
        timeline = SceneTimeline(
            timeline_id=f"{song_id}_timeline_phrases",
            song_id=song_id,
            duration=duration,
            scenes=scenes,
            auto_generated=True,
            generation_method="phrases",
        )
        
        return timeline
    
    def generate_from_beats(
        self,
        song_id: str,
        duration: float,
        beat_times: List[float],
        scenes_per_beat_group: int = 4,
        base_seed: int = 0,
    ) -> SceneTimeline:
        """
        Epic 09.B3: Generate timeline from beat grouping.
        
        Group beats and create one scene per group.
        
        Args:
            song_id: Source song ID
            duration: Song duration in seconds
            beat_times: List of beat times in seconds
            scenes_per_beat_group: How many beats per scene (e.g., 4 for 1 bar)
            base_seed: Base seed for deterministic randomness
            
        Returns:
            Auto-generated SceneTimeline
        """
        scenes = []
        
        # Group beats
        beat_groups = [
            beat_times[i:i + scenes_per_beat_group]
            for i in range(0, len(beat_times), scenes_per_beat_group)
        ]
        
        for i, group in enumerate(beat_groups):
            if not group:
                continue
            
            start_time = group[0]
            end_time = group[-1] + (beat_times[1] - beat_times[0] if len(beat_times) > 1 else 0.5)
            
            # Cycle through presets
            preset_id = self.available_presets[i % len(self.available_presets)]
            
            # Deterministic seed
            seed = base_seed ^ (i * 61)
            
            scene = Scene(
                scene_id=f"{song_id}_scene_{i}",
                start_time=start_time,
                end_time=min(end_time, duration),
                start_beat=group[0] if isinstance(group[0], int) else None,
                preset_id=preset_id,
                seed=seed,
                params={},
                intensity=1.0,
                metadata={
                    "beat_group_index": i,
                    "beats_in_group": len(group),
                },
                is_auto_generated=True,
            )
            scenes.append(scene)
        
        timeline = SceneTimeline(
            timeline_id=f"{song_id}_timeline_beats",
            song_id=song_id,
            duration=duration,
            scenes=scenes,
            auto_generated=True,
            generation_method="beats",
        )
        
        return timeline


def merge_scene_override(
    auto_scene: Scene,
    override: Optional[Scene],
) -> Scene:
    """
    Epic 09.B4: Merge auto-generated scene with manual override.
    
    Override shadows auto-generated defaults but doesn't break timeline.
    
    Args:
        auto_scene: Auto-generated baseline scene
        override: Manual override (or None)
        
    Returns:
        Merged scene with overrides applied
    """
    if override is None:
        return auto_scene
    
    # Create merged scene
    merged = auto_scene.model_copy(deep=True)
    
    # Apply overrides
    if override.preset_id:
        merged.preset_id = override.preset_id
    if override.seed != 0:
        merged.seed = override.seed
    if override.params:
        merged.params.update(override.params)
    if override.intensity != 1.0:
        merged.intensity = override.intensity
    if override.intensity_automation:
        merged.intensity_automation = override.intensity_automation
    if override.param_automation:
        merged.param_automation.update(override.param_automation)
    
    merged.is_manual_override = True
    
    return merged
