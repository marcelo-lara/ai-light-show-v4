"""
Specialized Shader Layers

Epic 07: Raindrops Shader
Epic 08: Spectroid Chase Shader
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from .layers import Layer, RenderContext, CANVAS_WIDTH, CANVAS_HEIGHT


@dataclass
class POIPoint:
    """Point of Interest definition."""
    x: float
    y: float
    name: str


class RaindropsLayer(Layer):
    """
    Epic 07: Raindrops shader - POI-aware radial pulse layer.
    
    Renders pulses originating from, passing through, and colliding at configured POIs.
    """
    
    def __init__(self):
        super().__init__("raindrops", "Raindrops")
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "pulse_rate": {"type": "float", "default": 2.0, "min": 0.1, "max": 10.0},
            "pulse_radius_growth": {"type": "float", "default": 5.0, "min": 1.0, "max": 20.0},
            "pulse_decay": {"type": "float", "default": 0.95, "min": 0.5, "max": 1.0},
            "collision_strength": {"type": "float", "default": 1.5, "min": 0.5, "max": 3.0},
            "base_color": {"type": "color", "default": "#00FFFF"},
            "poi_ids": {"type": "string", "default": "all"},  # "all" or comma-separated POI IDs
        }
    
    def render_frame(
        self,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT
    ) -> np.ndarray:
        """
        Epic 07.B1-B5: Render raindrops effect.
        
        Creates radial pulses from POIs with transit and collision behavior.
        """
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        pulse_rate = params.get("pulse_rate", 2.0)
        pulse_radius_growth = params.get("pulse_radius_growth", 5.0)
        pulse_decay = params.get("pulse_decay", 0.95)
        collision_strength = params.get("collision_strength", 1.5)
        base_color_hex = params.get("base_color", "#00FFFF")
        poi_ids_str = params.get("poi_ids", "all")
        pois = params.get("_pois", [])  # Internal: passed POI list
        
        base_color = self._parse_color(base_color_hex)
        
        # Generate pulses from POIs based on time
        pulse_time = context.frame_time * pulse_rate
        num_pulses = int(pulse_time) + 1
        
        decay_factor = pulse_decay ** context.frame_index
        
        for poi_idx, poi in enumerate(pois):
            # Generate pulses at this POI
            for pulse_num in range(max(0, num_pulses - 3), num_pulses + 1):
                pulse_age = pulse_time - pulse_num
                if pulse_age < 0 or pulse_age > 20:  # Skip old/future pulses
                    continue
                
                # Epic 07.B3: Transit behavior - pulses pass through POIs
                # For now, simple implementation: pulses expand from POI
                pulse_radius = pulse_age * pulse_radius_growth
                
                # Render pulse circle from this POI
                for y in range(height):
                    for x in range(width):
                        dist = math.sqrt((x - poi["x"]) ** 2 + (y - poi["y"]) ** 2)
                        
                        # Soft circle falloff
                        if dist <= pulse_radius + 5:
                            intensity = max(0, 1.0 - (dist - pulse_radius) / 5.0)
                            if intensity > 0:
                                value = int(255 * intensity * decay_factor)
                                frame[y, x] = [c * value // 255 for c in base_color]
        
        return frame
    
    @staticmethod
    def _parse_color(hex_color: str) -> Tuple[int, int, int]:
        """Parse hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class SpectroidChaseLayer(Layer):
    """
    Epic 08: Spectroid Chase shader - note/chord-reactive chase from parcan anchors.
    
    Generates outward lines from parcan fixtures that moving heads can follow.
    """
    
    def __init__(self):
        super().__init__("spectroid_chase", "Spectroid Chase")
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "trigger_sensitivity": {"type": "float", "default": 0.5, "min": 0.0, "max": 1.0},
            "line_length": {"type": "float", "default": 30.0, "min": 5.0, "max": 60.0},
            "chase_speed": {"type": "float", "default": 20.0, "min": 5.0, "max": 50.0},
            "fade_distance": {"type": "float", "default": 10.0, "min": 1.0, "max": 30.0},
            "line_width": {"type": "int", "default": 2, "min": 1, "max": 5},
            "base_color": {"type": "color", "default": "#FF00FF"},
            "parcan_ids": {"type": "string", "default": "all"},
        }
    
    def render_frame(
        self,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT
    ) -> np.ndarray:
        """
        Epic 08.B1-B5: Render spectroid chase effect.
        
        Creates lines from parcan positions based on audio triggers.
        """
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        trigger_sensitivity = params.get("trigger_sensitivity", 0.5)
        line_length = params.get("line_length", 30.0)
        chase_speed = params.get("chase_speed", 20.0)
        fade_distance = params.get("fade_distance", 10.0)
        line_width = params.get("line_width", 2)
        base_color_hex = params.get("base_color", "#FF00FF")
        parcan_ids_str = params.get("parcan_ids", "all")
        parcans = params.get("_parcans", [])  # Internal: passed parcan list
        
        base_color = self._parse_color(base_color_hex)
        
        # Check for trigger (onset or strong spectral content)
        trigger_active = context.onset_detected
        if not trigger_active and context.fft_bands:
            # Check if any FFT band exceeds threshold
            max_band = max(context.fft_bands)
            trigger_active = max_band > trigger_sensitivity
        
        # Draw lines from parcan anchors
        if trigger_active:
            for parcan in parcans:
                start_x = parcan.get("x", 50)
                start_y = parcan.get("y", 25)
                
                # Generate outward chase lines in 8 directions
                directions = self._get_chase_directions()
                
                for dx, dy in directions:
                    # Draw line from parcan outward
                    for dist in range(int(line_length)):
                        end_x = start_x + dx * dist
                        end_y = start_y + dy * dist
                        
                        # Check bounds
                        if not (0 <= end_x < width and 0 <= end_y < height):
                            continue
                        
                        # Fade intensity based on distance
                        fade_intensity = max(0, 1.0 - dist / fade_distance)
                        
                        # Age-based decay
                        age_decay = 0.95 ** context.frame_index
                        
                        intensity = int(255 * fade_intensity * age_decay)
                        if intensity > 0:
                            self._draw_thick_line(
                                frame, int(start_x), int(start_y),
                                int(end_x), int(end_y),
                                base_color, intensity, line_width
                            )
        
        return frame
    
    @staticmethod
    def _parse_color(hex_color: str) -> Tuple[int, int, int]:
        """Parse hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def _get_chase_directions() -> List[Tuple[float, float]]:
        """Get 8 cardinal directions for chase lines."""
        return [
            (1, 0),    # Right
            (-1, 0),   # Left
            (0, 1),    # Down
            (0, -1),   # Up
            (1, 1),    # Down-right
            (1, -1),   # Up-right
            (-1, 1),   # Down-left
            (-1, -1),  # Up-left
        ]
    
    @staticmethod
    def _draw_thick_line(
        frame: np.ndarray,
        x0: int, y0: int,
        x1: int, y1: int,
        color: Tuple[int, int, int],
        intensity: int,
        width: int
    ) -> None:
        """Draw a thick line on the frame."""
        # Bresenham line algorithm with thickness
        height, canvas_width, _ = frame.shape
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x1 > x0 else -1
        sy = 1 if y1 > y0 else -1
        err = dx - dy
        
        x, y = x0, y0
        while True:
            # Draw thick point
            for ox in range(-width//2, width//2 + 1):
                for oy in range(-width//2, width//2 + 1):
                    px, py = x + ox, y + oy
                    if 0 <= px < canvas_width and 0 <= py < height:
                        c = tuple(min(255, frame[py, px, i] + color[i] * intensity // 255) for i in range(3))
                        frame[py, px] = c
            
            if x == x1 and y == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
