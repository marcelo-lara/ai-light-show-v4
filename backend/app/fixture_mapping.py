"""
Fixture Mapping and Export

Epic 11: Fixture Mapping and Export functionality
- B1: Canonical pixel order documentation and encoding
- B2: Fixture reference schema
- B3: POI reference schema  
- B4: Mapping config definition
- B5: Linear mapping support
- B6: Serpentine mapping support
- B7: Export manifest v1
- B8: Gamma correction
- B9: Brightness limiting
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from pydantic import BaseModel, ConfigDict


class MappingType(str, Enum):
    """Supported pixel ordering types."""
    LINEAR = "linear"
    SERPENTINE = "serpentine"
    CUSTOM = "custom"


class PixelOrder(str, Enum):
    """Canonical pixel order definition (Epic 11.B1)."""
    # Row-major, origin at top-left (0,0)
    # Increases left-to-right, then top-to-bottom
    ROW_MAJOR_TOP_LEFT = "row_major_top_left"


@dataclass
class CanonicalPixelInfo:
    """
    Epic 11.B1: Canonical pixel order information.
    
    Documents the origin and row-major pixel order for the 100x50 canvas.
    """
    origin: str = "top_left"  # (0, 0) at top-left corner
    width: int = 100
    height: int = 50
    total_pixels: int = 5000
    axis_x: str = "left_to_right"  # X increases left to right
    axis_y: str = "top_to_bottom"  # Y increases top to bottom
    pixel_order: PixelOrder = PixelOrder.ROW_MAJOR_TOP_LEFT
    
    def get_linear_index(self, x: int, y: int) -> int:
        """Convert 2D coordinates to linear index."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(f"Coordinates ({x}, {y}) out of bounds [{self.width}x{self.height}]")
        return y * self.width + x
    
    def get_xy_from_linear(self, index: int) -> Tuple[int, int]:
        """Convert linear index back to 2D coordinates."""
        if not (0 <= index < self.total_pixels):
            raise ValueError(f"Index {index} out of bounds [0-{self.total_pixels}]")
        y = index // self.width
        x = index % self.width
        return (x, y)


class FixtureMapping(BaseModel):
    """
    Epic 11.B4: Mapping configuration.
    
    Defines how fixture output maps to canvas pixels.
    """
    model_config = ConfigDict(use_enum_values=False)
    
    mapping_id: str
    fixture_id: str
    fixture_type: str
    
    # Physical location on the canvas
    canvas_anchor_x: float  # 0.0-1.0
    canvas_anchor_y: float  # 0.0-1.0
    
    # Pixel layout for this fixture
    pixel_width: int  # Number of columns of pixels
    pixel_height: int  # Number of rows of pixels
    
    # Mapping type
    mapping_type: MappingType = MappingType.LINEAR
    
    # Reversal options
    reverse_x: bool = False
    reverse_y: bool = False
    
    # Optional: per-fixture calibration reference
    calibration_poi_id: Optional[str] = None


class PixelMappingEngine:
    """
    Epic 11.B5-B6: Pixel mapping engine supporting linear and serpentine orders.
    
    Handles conversion between fixture pixel space and canvas coordinate space.
    """
    
    def __init__(self):
        self.canonical = CanonicalPixelInfo()
    
    def linear_mapping(
        self,
        fixture_pixels: np.ndarray,  # Shape: (height, width, 3)
        mapping: FixtureMapping,
    ) -> List[Tuple[int, int, Tuple[int, int, int]]]:
        """
        Epic 11.B5: Linear mapping of fixture pixels to canvas.
        
        Maps fixture pixels in row-major order starting from anchor point.
        
        Args:
            fixture_pixels: RGB pixel data from fixture
            mapping: Mapping configuration
            
        Returns:
            List of (canvas_x, canvas_y, (r, g, b)) tuples
        """
        results = []
        height, width = fixture_pixels.shape[0:2]
        
        # Convert anchor (0.0-1.0) to canvas coordinates
        canvas_start_x = int(mapping.canvas_anchor_x * self.canonical.width)
        canvas_start_y = int(mapping.canvas_anchor_y * self.canonical.height)
        
        for y in range(height):
            for x in range(width):
                # Apply reversal
                fx = (width - 1 - x) if mapping.reverse_x else x
                fy = (height - 1 - y) if mapping.reverse_y else y
                
                # Calculate canvas position
                canvas_x = canvas_start_x + fx
                canvas_y = canvas_start_y + fy
                
                # Bounds check
                if 0 <= canvas_x < self.canonical.width and 0 <= canvas_y < self.canonical.height:
                    pixel = fixture_pixels[y, x]
                    rgb = tuple(int(p) for p in pixel[:3])
                    results.append((canvas_x, canvas_y, rgb))
        
        return results
    
    def serpentine_mapping(
        self,
        fixture_pixels: np.ndarray,  # Shape: (height, width, 3)
        mapping: FixtureMapping,
    ) -> List[Tuple[int, int, Tuple[int, int, int]]]:
        """
        Epic 11.B6: Serpentine mapping of fixture pixels to canvas.
        
        Maps fixture pixels in serpentine (boustrophedon) order:
        odd rows go left-to-right, even rows go right-to-left.
        
        Args:
            fixture_pixels: RGB pixel data from fixture
            mapping: Mapping configuration
            
        Returns:
            List of (canvas_x, canvas_y, (r, g, b)) tuples
        """
        results = []
        height, width = fixture_pixels.shape[0:2]
        
        # Convert anchor (0.0-1.0) to canvas coordinates
        canvas_start_x = int(mapping.canvas_anchor_x * self.canonical.width)
        canvas_start_y = int(mapping.canvas_anchor_y * self.canonical.height)
        
        for y in range(height):
            for x in range(width):
                # Serpentine: alternate direction based on row
                if y % 2 == 0:
                    # Even rows: left-to-right
                    fx = (width - 1 - x) if mapping.reverse_x else x
                else:
                    # Odd rows: right-to-left (serpentine)
                    fx = x if mapping.reverse_x else (width - 1 - x)
                
                fy = (height - 1 - y) if mapping.reverse_y else y
                
                # Calculate canvas position
                canvas_x = canvas_start_x + fx
                canvas_y = canvas_start_y + fy
                
                # Bounds check
                if 0 <= canvas_x < self.canonical.width and 0 <= canvas_y < self.canonical.height:
                    pixel = fixture_pixels[y, x]
                    rgb = tuple(int(p) for p in pixel[:3])
                    results.append((canvas_x, canvas_y, rgb))
        
        return results
    
    def apply_mapping(
        self,
        fixture_pixels: np.ndarray,
        mapping: FixtureMapping,
    ) -> List[Tuple[int, int, Tuple[int, int, int]]]:
        """Apply appropriate mapping based on type."""
        if mapping.mapping_type == MappingType.LINEAR:
            return self.linear_mapping(fixture_pixels, mapping)
        elif mapping.mapping_type == MappingType.SERPENTINE:
            return self.serpentine_mapping(fixture_pixels, mapping)
        else:
            # Default to linear
            return self.linear_mapping(fixture_pixels, mapping)


@dataclass
class GammaCorrection:
    """
    Epic 11.B8: Gamma correction configuration.
    """
    enabled: bool = True
    gamma: float = 2.2  # Standard display gamma
    
    def apply(self, value: int) -> int:
        """
        Apply gamma correction to a single color channel.
        
        Args:
            value: Color value (0-255)
            
        Returns:
            Gamma-corrected value (0-255)
        """
        if not self.enabled:
            return value
        
        normalized = value / 255.0
        corrected = pow(normalized, 1.0 / self.gamma)
        return int(corrected * 255)
    
    def apply_rgb(self, rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Apply gamma to all channels."""
        return (
            self.apply(rgb[0]),
            self.apply(rgb[1]),
            self.apply(rgb[2]),
        )


@dataclass
class BrightnessLimiter:
    """
    Epic 11.B9: Brightness limiting configuration.
    """
    enabled: bool = True
    max_brightness: float = 1.0  # 0.0-1.0
    
    def apply(self, rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Limit overall brightness of a color.
        
        Args:
            rgb: Color tuple
            
        Returns:
            Brightness-limited color tuple
        """
        if not self.enabled:
            return rgb
        
        # Calculate perceived brightness (luminance)
        r, g, b = rgb
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
        
        if luminance > self.max_brightness:
            scale = self.max_brightness / luminance
            return (
                int(r * scale),
                int(g * scale),
                int(b * scale),
            )
        
        return rgb


class ExportFrame(BaseModel):
    """
    Epic 11.B7: Single frame in export manifest.
    
    Contains fixture-ordered pixel data for a frame.
    """
    frame_index: int
    fixture_frames: Dict[str, List[Tuple[int, int, int]]]  # fixture_id -> [(x, y, (r,g,b)), ...]
    timestamp_ms: float


class ExportManifest(BaseModel):
    """
    Epic 11.B7: Export manifest v1.
    
    Complete mapped frame data and metadata for export to downstream systems.
    """
    manifest_version: str = "1.0"
    render_id: str
    song_id: str
    
    # Metadata
    fps: int
    duration_sec: float
    total_frames: int
    
    # Canonical info
    canonical_pixel_info: Dict[str, Any]
    
    # Fixture mappings used
    fixture_mappings: List[Dict[str, Any]]
    
    # Processing applied
    gamma_correction: Dict[str, Any]
    brightness_limiting: Dict[str, Any]
    
    # Frame data references
    frame_data_path: Optional[str] = None  # Path to binary frame data file
    frames_count: int = 0


class ExportEngine:
    """
    Epic 11: Complete export engine combining mapping, gamma, and brightness limiting.
    """
    
    def __init__(
        self,
        gamma_correction: Optional[GammaCorrection] = None,
        brightness_limiter: Optional[BrightnessLimiter] = None,
    ):
        self.mapping_engine = PixelMappingEngine()
        self.gamma_correction = gamma_correction or GammaCorrection()
        self.brightness_limiter = brightness_limiter or BrightnessLimiter()
        self.canonical = CanonicalPixelInfo()
    
    def export_frame(
        self,
        render_frame: np.ndarray,  # Shape: (50, 100, 3)
        fixture_mappings: List[FixtureMapping],
    ) -> ExportFrame:
        """
        Export a single render frame with fixture mapping applied.
        
        Args:
            render_frame: Rendered canvas frame
            fixture_mappings: List of fixture mappings to apply
            
        Returns:
            ExportFrame with mapped fixture data
        """
        fixture_frames: Dict[str, List[Tuple[int, int, int]]] = {}
        
        # Apply each fixture mapping
        for mapping in fixture_mappings:
            # For now, use the entire render_frame as fixture pixels
            # In production, this would extract the fixture's view from the render
            mapped_pixels = self.mapping_engine.apply_mapping(render_frame, mapping)
            
            # Apply post-processing (gamma, brightness)
            processed_pixels = []
            for x, y, rgb in mapped_pixels:
                rgb = self.gamma_correction.apply_rgb(rgb)
                rgb = self.brightness_limiter.apply(rgb)
                processed_pixels.append((x, y, rgb))
            
            fixture_frames[mapping.fixture_id] = processed_pixels
        
        return ExportFrame(
            frame_index=0,
            fixture_frames=fixture_frames,
            timestamp_ms=0.0,
        )
    
    def create_export_manifest(
        self,
        render_id: str,
        song_id: str,
        fps: int,
        duration_sec: float,
        total_frames: int,
        fixture_mappings: List[FixtureMapping],
    ) -> ExportManifest:
        """
        Create an export manifest for a render.
        
        Args:
            render_id: ID of the render
            song_id: ID of the song
            fps: Frames per second
            duration_sec: Duration in seconds
            total_frames: Total number of frames
            fixture_mappings: List of fixture mappings
            
        Returns:
            ExportManifest ready for export
        """
        return ExportManifest(
            render_id=render_id,
            song_id=song_id,
            fps=fps,
            duration_sec=duration_sec,
            total_frames=total_frames,
            canonical_pixel_info={
                "origin": self.canonical.origin,
                "width": self.canonical.width,
                "height": self.canonical.height,
                "pixel_order": self.canonical.pixel_order.value,
            },
            fixture_mappings=[m.model_dump() for m in fixture_mappings],
            gamma_correction={
                "enabled": self.gamma_correction.enabled,
                "gamma": self.gamma_correction.gamma,
            },
            brightness_limiting={
                "enabled": self.brightness_limiter.enabled,
                "max_brightness": self.brightness_limiter.max_brightness,
            },
        )
