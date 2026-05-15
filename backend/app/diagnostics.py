"""
Render Diagnostics Implementation

Epic 12: Backend track for render diagnostics
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from PIL import Image


@dataclass
class DiagnosticsSummary:
    """
    Epic 12.B1: Diagnostics summary metrics
    
    Computes brightness, average color, frame delta, blank-frame warnings,
    and render duration.
    """
    brightness_avg: float
    brightness_min: float
    brightness_max: float
    color_avg: tuple  # (R, G, B)
    frame_delta_avg: float  # Average pixel change between frames
    blank_frame_count: int
    static_frame_count: int
    render_duration_ms: float
    total_frames: int


@dataclass
class VarietyMetrics:
    """
    Epic 12.B2: Variety metrics for beat-response and section variation
    
    Flags static or repetitive renders.
    """
    beat_response_score: float  # 0.0-1.0
    section_variation_score: float  # 0.0-1.0
    is_static: bool
    is_repetitive: bool
    warnings: List[str]


class DiagnosticsAnalyzer:
    """
    Service for analyzing render artifacts and generating diagnostics.
    """
    
    BLANK_FRAME_THRESHOLD = 0.01  # 1% brightness
    STATIC_FRAME_THRESHOLD = 0.99  # 99% similarity
    
    def __init__(self):
        self.frame_history: List[np.ndarray] = []
    
    def analyze_frames(self, frames: List[np.ndarray]) -> DiagnosticsSummary:
        """
        Epic 12.B1: Analyze frame sequence for diagnostics.
        
        Args:
            frames: List of RGB frame arrays (each 100x50x3)
            
        Returns:
            DiagnosticsSummary with computed metrics
        """
        if not frames:
            return DiagnosticsSummary(
                brightness_avg=0.0,
                brightness_min=0.0,
                brightness_max=0.0,
                color_avg=(0, 0, 0),
                frame_delta_avg=0.0,
                blank_frame_count=0,
                static_frame_count=0,
                render_duration_ms=0.0,
                total_frames=0,
            )
        
        frames_array = np.array(frames, dtype=np.float32) / 255.0
        
        # Brightness metrics
        brightness = np.mean(frames_array, axis=(1, 2, 3))  # Per-frame brightness
        brightness_avg = np.mean(brightness)
        brightness_min = np.min(brightness)
        brightness_max = np.max(brightness)
        
        # Average color
        color_avg_normalized = np.mean(frames_array, axis=(0, 1, 2))
        color_avg = tuple(int(c * 255) for c in color_avg_normalized)
        
        # Frame delta (pixel-wise differences)
        frame_deltas = []
        for i in range(1, len(frames_array)):
            delta = np.mean(np.abs(frames_array[i] - frames_array[i-1]))
            frame_deltas.append(delta)
        frame_delta_avg = np.mean(frame_deltas) if frame_deltas else 0.0
        
        # Blank frames
        blank_frame_count = sum(1 for b in brightness if b < self.BLANK_FRAME_THRESHOLD)
        
        # Static frames
        static_frame_count = sum(1 for delta in frame_deltas if delta < (1.0 - self.STATIC_FRAME_THRESHOLD))
        
        return DiagnosticsSummary(
            brightness_avg=float(brightness_avg),
            brightness_min=float(brightness_min),
            brightness_max=float(brightness_max),
            color_avg=color_avg,
            frame_delta_avg=float(frame_delta_avg),
            blank_frame_count=blank_frame_count,
            static_frame_count=static_frame_count,
            render_duration_ms=0.0,  # Would be set by caller
            total_frames=len(frames),
        )
    
    def analyze_variety(self, summary: DiagnosticsSummary) -> VarietyMetrics:
        """
        Epic 12.B2: Analyze beat-response and section variation.
        
        Args:
            summary: DiagnosticsSummary from frame analysis
            
        Returns:
            VarietyMetrics with scores and warnings
        """
        warnings: List[str] = []
        
        # Beat response score: based on frame delta (higher is better)
        beat_response_score = min(1.0, summary.frame_delta_avg * 2.0)
        
        # Section variation: based on brightness range
        brightness_range = summary.brightness_max - summary.brightness_min
        section_variation_score = min(1.0, brightness_range)
        
        is_static = beat_response_score < 0.1
        is_repetitive = summary.static_frame_count > (summary.total_frames * 0.5)
        
        if summary.blank_frame_count > (summary.total_frames * 0.3):
            warnings.append("High number of blank frames detected")
        
        if is_static:
            warnings.append("Render appears static - low frame-to-frame variation")
        
        if is_repetitive:
            warnings.append("Render appears repetitive - insufficient variation")
        
        return VarietyMetrics(
            beat_response_score=beat_response_score,
            section_variation_score=section_variation_score,
            is_static=is_static,
            is_repetitive=is_repetitive,
            warnings=warnings,
        )
    
    def generate_contact_sheet(
        self,
        frames: List[np.ndarray],
        grid_size: int = 5,
        frame_width: int = 100,
        frame_height: int = 50,
    ) -> Image.Image:
        """
        Epic 12.B3: Generate contact sheet of sampled frames.
        
        Args:
            frames: List of RGB frames
            grid_size: NxN grid of frames to show
            frame_width: Width of each frame in pixels
            frame_height: Height of each frame in pixels
            
        Returns:
            PIL Image of contact sheet
        """
        if not frames:
            return Image.new('RGB', (100, 100), color='black')
        
        grid_count = grid_size * grid_size
        step = max(1, len(frames) // grid_count)
        sampled_frames = frames[::step][:grid_count]
        
        # Pad with black frames if needed
        while len(sampled_frames) < grid_count:
            sampled_frames.append(np.zeros((frame_height, frame_width, 3), dtype=np.uint8))
        
        # Create contact sheet
        sheet_width = frame_width * grid_size
        sheet_height = frame_height * grid_size
        sheet = Image.new('RGB', (sheet_width, sheet_height))
        
        for idx, frame in enumerate(sampled_frames[:grid_count]):
            row = (idx // grid_size) * frame_height
            col = (idx % grid_size) * frame_width
            
            frame_img = Image.fromarray(frame.astype(np.uint8), 'RGB')
            frame_img = frame_img.resize((frame_width, frame_height))
            sheet.paste(frame_img, (col, row))
        
        return sheet
    
    def generate_preview_gif(
        self,
        frames: List[np.ndarray],
        frame_count: int = 60,
        duration: int = 50,  # ms per frame
    ) -> Image.Image:
        """
        Epic 12.B4: Generate preview GIF or strip.
        
        Args:
            frames: List of RGB frames
            frame_count: Number of frames to include in preview
            duration: Milliseconds per frame in GIF
            
        Returns:
            PIL Image (first frame) - in production, would save as GIF
        """
        if not frames:
            return Image.new('RGB', (50, 100), color='black')
        
        step = max(1, len(frames) // frame_count)
        sampled = frames[::step][:frame_count]
        
        # Return first frame (in production, save as GIF)
        first_frame = Image.fromarray(sampled[0].astype(np.uint8), 'RGB')
        return first_frame


class DiagnosticsReport:
    """
    Epic 12: Complete diagnostics report for a render.
    """
    
    def __init__(
        self,
        render_id: str,
        summary: DiagnosticsSummary,
        variety: VarietyMetrics,
    ):
        self.render_id = render_id
        self.summary = summary
        self.variety = variety
        self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "render_id": self.render_id,
            "created_at": self.created_at.isoformat(),
            "summary": {
                "brightness_avg": self.summary.brightness_avg,
                "brightness_min": self.summary.brightness_min,
                "brightness_max": self.summary.brightness_max,
                "color_avg": self.summary.color_avg,
                "frame_delta_avg": self.summary.frame_delta_avg,
                "blank_frame_count": self.summary.blank_frame_count,
                "static_frame_count": self.summary.static_frame_count,
                "total_frames": self.summary.total_frames,
            },
            "variety": {
                "beat_response_score": self.variety.beat_response_score,
                "section_variation_score": self.variety.section_variation_score,
                "is_static": self.variety.is_static,
                "is_repetitive": self.variety.is_repetitive,
                "warnings": self.variety.warnings,
            },
        }
