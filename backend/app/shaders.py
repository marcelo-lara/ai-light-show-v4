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

    Pulses originate from configured POIs (07.B1-B2), pass through intermediate
    POIs creating a transit brightness boost (07.B3), and produce a deterministic
    collision effect where two pulse fronts meet (07.B4).  Registered in the
    LayerRegistry so presets can use it directly (07.B6).
    """

    def __init__(self):
        super().__init__("raindrops", "Raindrops")

    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "pulse_rate": {"type": "float", "default": 2.0, "min": 0.1, "max": 10.0},
            "pulse_radius_growth": {"type": "float", "default": 5.0, "min": 1.0, "max": 20.0},
            "pulse_decay": {"type": "float", "default": 0.95, "min": 0.5, "max": 1.0},
            "collision_strength": {"type": "float", "default": 1.5, "min": 0.5, "max": 3.0},
            "transit_boost": {"type": "float", "default": 1.8, "min": 1.0, "max": 3.0},
            "base_color": {"type": "color", "default": "#00FFFF"},
            "poi_ids": {"type": "string", "default": "all"},
        }

    def render_frame(
        self,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT,
    ) -> np.ndarray:
        """
        Epic 07.B1-B5: Render raindrops with transit (B3) and collision (B4) behavior.

        Uses a float32 intensity accumulator so that overlapping pulses from
        different POIs naturally add up.  Pixels where the accumulated intensity
        exceeds 1.0 are the collision sites; they are boosted before clamping to
        produce the collision flash effect (B4).  Transit events are implemented
        as a brief intensity spike at every *other* POI location whenever a pulse
        front from a *different* POI passes through it (B3).
        """
        pulse_rate = params.get("pulse_rate", 2.0)
        pulse_radius_growth = params.get("pulse_radius_growth", 5.0)
        pulse_decay = params.get("pulse_decay", 0.95)
        collision_strength = params.get("collision_strength", 1.5)
        transit_boost = params.get("transit_boost", 1.8)
        base_color = self._parse_color(params.get("base_color", "#00FFFF"))
        pois: List[Dict[str, Any]] = params.get("_pois", [])

        if not pois:
            pois = [{"x": width // 2, "y": height // 2, "id": "center"}]

        pulse_time = context.frame_time * pulse_rate
        sigma = max(0.5, pulse_radius_growth * 0.6)  # Gaussian ring width

        # Float accumulator: separate per-source so collision detection works
        ys, xs = np.meshgrid(np.arange(height), np.arange(width), indexing="ij")
        per_source = np.zeros((len(pois), height, width), dtype=np.float32)

        for src_idx, src_poi in enumerate(pois):
            poi_x = float(src_poi.get("x", width // 2))
            poi_y = float(src_poi.get("y", height // 2))
            dist_map = np.sqrt((xs - poi_x) ** 2 + (ys - poi_y) ** 2)

            for pulse_num in range(max(0, int(pulse_time) - 4), int(pulse_time) + 2):
                pulse_age = pulse_time - pulse_num
                if pulse_age < 0 or pulse_age > (max(width, height) / pulse_radius_growth + 2):
                    continue
                pulse_radius = pulse_age * pulse_radius_growth
                # Gaussian ring centred at pulse_radius
                ring = np.exp(-((dist_map - pulse_radius) ** 2) / (2 * sigma ** 2))
                # Temporal envelope: pulses fade as they age
                time_envelope = max(0.0, 1.0 - pulse_age / (max(width, height) / pulse_radius_growth + 1))
                per_source[src_idx] += ring * time_envelope

            # Epic 07.B3: transit boost — when this source's current pulse front
            # passes through each *other* POI, add a brief spike at that POI pixel.
            for other in pois:
                if other is src_poi:
                    continue
                ox, oy = float(other.get("x", 0)), float(other.get("y", 0))
                inter_dist = math.sqrt((poi_x - ox) ** 2 + (poi_y - oy) ** 2)
                # Current pulse front radius
                current_radius = (pulse_time % 1.0) * pulse_radius_growth + (int(pulse_time) % max(1, int(max(width, height) / pulse_radius_growth))) * pulse_radius_growth
                for pulse_num in range(max(0, int(pulse_time) - 4), int(pulse_time) + 2):
                    pulse_age = pulse_time - pulse_num
                    if pulse_age < 0:
                        continue
                    r = pulse_age * pulse_radius_growth
                    proximity = abs(r - inter_dist)
                    if proximity < sigma * 2:
                        boost_intensity = transit_boost * math.exp(-(proximity ** 2) / (2 * sigma ** 2))
                        py0 = max(0, int(oy) - 3)
                        py1 = min(height, int(oy) + 4)
                        px0 = max(0, int(ox) - 3)
                        px1 = min(width, int(ox) + 4)
                        per_source[src_idx, py0:py1, px0:px1] += boost_intensity

        # Sum across sources
        total = per_source.sum(axis=0)

        # Epic 07.B4: collision — pixels where multiple sources contribute above
        # threshold are brightened by collision_strength.
        source_count = (per_source > 0.05).sum(axis=0)
        collision_mask = source_count >= 2
        total = np.where(collision_mask, total * collision_strength, total)

        # Apply temporal decay based on frame index
        total *= pulse_decay ** (context.frame_index / max(1, context.fps))

        intensity = np.clip(total, 0.0, 1.0)[:, :, np.newaxis]
        frame = (np.array(base_color, dtype=np.float32) * intensity).astype(np.uint8)
        return frame

    @staticmethod
    def _parse_color(hex_color: str) -> Tuple[int, int, int]:
        """Parse hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class SpectroidChaseLayer(Layer):
    """
    Epic 08: Spectroid Chase shader - note/chord-reactive chase from parcan anchors.

    Generates outward chase lines from parcan fixtures (08.B1-B4, B6) and exposes
    structured moving-head follow-line data (08.B5) so DMX/moving-head drivers can
    read the active line directions without re-deriving them from pixel data.
    Registered in LayerRegistry for preset use (08.B7).
    """

    def __init__(self):
        super().__init__("spectroid_chase", "Spectroid Chase")
        # Epic 08.B5: cache last-rendered follow targets for downstream consumers
        self._last_follow_targets: List[Dict[str, Any]] = []

    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "trigger_sensitivity": {"type": "float", "default": 0.5, "min": 0.0, "max": 1.0},
            "line_length": {"type": "float", "default": 30.0, "min": 5.0, "max": 60.0},
            "chase_speed": {"type": "float", "default": 20.0, "min": 5.0, "max": 50.0},
            "fade_distance": {"type": "float", "default": 10.0, "min": 1.0, "max": 30.0},
            "line_width": {"type": "int", "default": 2, "min": 1, "max": 5},
            "base_color": {"type": "color", "default": "#FF00FF"},
            "parcan_ids": {"type": "string", "default": "all"},
            "moving_head_follow": {"type": "boolean", "default": True},
        }

    def render_frame(
        self,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT,
    ) -> np.ndarray:
        """
        Epic 08.B1-B5: Render spectroid chase and build moving-head follow targets.
        """
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        trigger_sensitivity = params.get("trigger_sensitivity", 0.5)
        line_length = params.get("line_length", 30.0)
        fade_distance = params.get("fade_distance", 10.0)
        line_width = params.get("line_width", 2)
        base_color = self._parse_color(params.get("base_color", "#FF00FF"))
        parcans: List[Dict[str, Any]] = params.get("_parcans", [])
        expose_follow = params.get("moving_head_follow", True)

        trigger_active = context.onset_detected
        if not trigger_active and context.fft_bands:
            trigger_active = max(context.fft_bands) > trigger_sensitivity

        # Epic 08.B5: reset follow targets each frame
        follow_targets: List[Dict[str, Any]] = []

        if trigger_active:
            directions = self._get_chase_directions()
            for parcan in parcans:
                start_x = float(parcan.get("x", width // 2))
                start_y = float(parcan.get("y", height // 2))

                for dx, dy in directions:
                    # Clamp actual drawn length to canvas boundary
                    max_dist = int(line_length)
                    for dist in range(max_dist):
                        ex = start_x + dx * dist
                        ey = start_y + dy * dist
                        if not (0 <= ex < width and 0 <= ey < height):
                            max_dist = dist
                            break

                    if max_dist <= 0:
                        continue

                    end_x = start_x + dx * (max_dist - 1)
                    end_y = start_y + dy * (max_dist - 1)

                    # Full intensity at the anchor; age-based decay across frames.
                    age_decay = 0.95 ** context.frame_index
                    intensity = max(1, int(255 * age_decay))

                    self._draw_thick_line(
                        frame,
                        int(start_x), int(start_y),
                        int(end_x), int(end_y),
                        base_color, intensity, line_width,
                    )

                    # Epic 08.B5: record follow-line metadata per direction
                    if expose_follow:
                        angle_deg = math.degrees(math.atan2(dy, dx))
                        follow_targets.append({
                            "parcan_x": start_x,
                            "parcan_y": start_y,
                            "direction_dx": dx,
                            "direction_dy": dy,
                            "angle_deg": angle_deg,
                            "line_length": max_dist,
                            "end_x": end_x,
                            "end_y": end_y,
                            "active": True,
                        })

        self._last_follow_targets = follow_targets
        return frame

    def get_moving_head_targets(self) -> List[Dict[str, Any]]:
        """
        Epic 08.B5: Return moving-head follow targets from the last rendered frame.

        Each entry describes one active chase line with its parcan anchor, direction
        vector, angle in degrees, and canvas endpoint.  Moving-head drivers can
        consume this without re-parsing pixel data.

        Returns:
            List of dicts with keys:
                parcan_x, parcan_y  – anchor fixture canvas position
                direction_dx, direction_dy – unit direction vector
                angle_deg           – line heading in degrees (0 = right)
                line_length         – number of pixels drawn
                end_x, end_y        – canvas endpoint
                active              – True if trigger was live when computed
        """
        return list(self._last_follow_targets)

    @staticmethod
    def _parse_color(hex_color: str) -> Tuple[int, int, int]:
        """Parse hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def _get_chase_directions() -> List[Tuple[float, float]]:
        """Get 8 cardinal and diagonal directions for chase lines."""
        return [
            (1.0, 0.0),
            (-1.0, 0.0),
            (0.0, 1.0),
            (0.0, -1.0),
            (0.7071, 0.7071),
            (0.7071, -0.7071),
            (-0.7071, 0.7071),
            (-0.7071, -0.7071),
        ]

    @staticmethod
    def _draw_thick_line(
        frame: np.ndarray,
        x0: int, y0: int,
        x1: int, y1: int,
        color: Tuple[int, int, int],
        intensity: int,
        width: int,
    ) -> None:
        """Draw a thick line using Bresenham's algorithm."""
        canvas_h, canvas_w, _ = frame.shape
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x1 > x0 else -1
        sy = 1 if y1 > y0 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            for ox in range(-width // 2, width // 2 + 1):
                for oy in range(-width // 2, width // 2 + 1):
                    px, py = x + ox, y + oy
                    if 0 <= px < canvas_w and 0 <= py < canvas_h:
                        frame[py, px] = tuple(
                            min(255, int(frame[py, px, i]) + color[i] * intensity // 255)
                            for i in range(3)
                        )
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
