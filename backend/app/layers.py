"""
Layer Library

Epic 04: Layer Library
Defines the layer registry, base layer interface, and built-in layer implementations.
"""

import random
import math
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import numpy as np


# Canvas dimensions
CANVAS_WIDTH = 100
CANVAS_HEIGHT = 50


@dataclass
class RenderContext:
    """
    Epic 04.B1: Deterministic render context for a layer.
    
    Provides seeded randomness and shared state for layer execution.
    """
    seed: int
    frame_index: int
    total_frames: int
    fps: int
    beat_progress: float = 0.0  # 0-1 within current beat
    bar_progress: float = 0.0   # 0-1 within current bar
    phrase_progress: float = 0.0  # 0-1 within phrase
    fft_bands: Optional[List[float]] = None
    onset_detected: bool = False
    
    def get_rng(self) -> random.Random:
        """Get seeded random number generator for deterministic output."""
        rng = random.Random()
        rng.seed(self.seed ^ self.frame_index)
        return rng
    
    @property
    def frame_time(self) -> float:
        """Get current frame time in seconds."""
        return self.frame_index / self.fps
    
    @property
    def total_time(self) -> float:
        """Get total duration in seconds."""
        return self.total_frames / self.fps


class Layer(ABC):
    """
    Epic 04.B1: Base layer interface.
    
    All layers implement this interface with deterministic seeded execution.
    """
    
    def __init__(self, layer_id: str, label: str):
        self.layer_id = layer_id
        self.label = label
    
    @abstractmethod
    def get_parameter_schema(self) -> Dict[str, Any]:
        """Return parameter schema for this layer."""
        pass
    
    @abstractmethod
    def render_frame(
        self,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT
    ) -> np.ndarray:
        """
        Render a single frame.
        
        Args:
            context: Render context with frame info and seeded randomness
            params: Layer parameters
            width: Canvas width
            height: Canvas height
        
        Returns:
            RGB array of shape (height, width, 3) with values 0-255
        """
        pass
    
    def render_batch(
        self,
        context_list: List[RenderContext],
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT
    ) -> List[np.ndarray]:
        """
        Render multiple frames efficiently.
        
        Default implementation calls render_frame for each context.
        Override for optimized batch rendering.
        """
        return [self.render_frame(ctx, params, width, height) for ctx in context_list]


class WaveLayer(Layer):
    """
    Epic 04.B2: Wave layer - migrated from hardcoded implementation.
    
    Renders sine waves moving left to right with configurable speed and amplitude.
    """
    
    def __init__(self):
        super().__init__("wave", "Wave")
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "speed": {"type": "float", "default": 1.0, "min": 0.1, "max": 5.0},
            "amplitude": {"type": "float", "default": 1.0, "min": 0.1, "max": 2.0},
            "wavelength": {"type": "int", "default": 20, "min": 5, "max": 50},
            "base_color": {"type": "color", "default": "#0000FF"},
        }
    
    def render_frame(
        self,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT
    ) -> np.ndarray:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        speed = params.get("speed", 1.0)
        amplitude = params.get("amplitude", 1.0)
        wavelength = params.get("wavelength", 20)
        base_color_hex = params.get("base_color", "#0000FF")
        
        # Parse hex color
        base_color = self._parse_color(base_color_hex)
        
        # Calculate wave offset based on frame time
        offset = (context.frame_time * speed * wavelength) % width
        
        # Render wave
        for x in range(width):
            phase = ((x - offset) / wavelength) * 2 * math.pi
            y_offset = math.sin(phase) * amplitude * height / 3
            y = int(height / 2 + y_offset)
            y = max(0, min(height - 1, y))
            
            if 0 <= y < height:
                intensity = int(255 * (0.5 + 0.5 * math.sin(phase)))
                frame[y, x] = [c * intensity // 255 for c in base_color]
        
        return frame
    
    @staticmethod
    def _parse_color(hex_color: str) -> Tuple[int, int, int]:
        """Parse hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class RadialPulseLayer(Layer):
    """
    Epic 04.B3: Radial pulse layer - migrated from hardcoded pulse.
    
    Renders expanding pulses from center or specified points.
    """
    
    def __init__(self):
        super().__init__("radial_pulse", "Radial Pulse")
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "center_x": {"type": "int", "default": 50, "min": 0, "max": 100},
            "center_y": {"type": "int", "default": 25, "min": 0, "max": 50},
            "pulse_speed": {"type": "float", "default": 10.0, "min": 1.0, "max": 50.0},
            "pulse_radius": {"type": "float", "default": 20.0, "min": 1.0, "max": 50.0},
            "decay": {"type": "float", "default": 0.95, "min": 0.5, "max": 1.0},
            "base_color": {"type": "color", "default": "#FFFFFF"},
        }
    
    def render_frame(
        self,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT
    ) -> np.ndarray:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        center_x = params.get("center_x", 50)
        center_y = params.get("center_y", 25)
        pulse_speed = params.get("pulse_speed", 10.0)
        pulse_radius = params.get("pulse_radius", 20.0)
        decay = params.get("decay", 0.95)
        base_color_hex = params.get("base_color", "#FFFFFF")
        
        base_color = WaveLayer._parse_color(base_color_hex)
        
        # Calculate expanding pulse radius
        pulse_front = (context.frame_time * pulse_speed) % (max(width, height) * 2)
        
        # Render pulse
        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                
                # Intensity based on distance from pulse front
                intensity = 0
                if dist <= pulse_front:
                    distance_from_front = pulse_front - dist
                    if distance_from_front <= pulse_radius:
                        intensity = int(255 * (1.0 - distance_from_front / pulse_radius) ** 2 * (decay ** context.frame_index))
                
                if intensity > 0:
                    frame[y, x] = [c * intensity // 255 for c in base_color]
        
        return frame


class SolidFieldLayer(Layer):
    """
    Epic 04.B4: Solid field layer - fills canvas with a solid color.
    """
    
    def __init__(self):
        super().__init__("solid_field", "Solid Field")
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "color": {"type": "color", "default": "#FFFFFF"},
            "intensity": {"type": "float", "default": 1.0, "min": 0.0, "max": 1.0},
        }
    
    def render_frame(
        self,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT
    ) -> np.ndarray:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        color_hex = params.get("color", "#FFFFFF")
        intensity = params.get("intensity", 1.0)
        
        base_color = WaveLayer._parse_color(color_hex)
        color_value = tuple(int(c * intensity) for c in base_color)
        
        frame[:, :] = color_value
        return frame


class GradientFieldLayer(Layer):
    """
    Epic 04.B5: Gradient field layer - renders linear gradient.
    """
    
    def __init__(self):
        super().__init__("gradient_field", "Gradient Field")
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "direction": {"type": "choice", "default": "horizontal", "choices": ["horizontal", "vertical", "diagonal"]},
            "color1": {"type": "color", "default": "#000000"},
            "color2": {"type": "color", "default": "#FFFFFF"},
        }
    
    def render_frame(
        self,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT
    ) -> np.ndarray:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        direction = params.get("direction", "horizontal")
        color1_hex = params.get("color1", "#000000")
        color2_hex = params.get("color2", "#FFFFFF")
        
        color1 = np.array(WaveLayer._parse_color(color1_hex), dtype=np.float32)
        color2 = np.array(WaveLayer._parse_color(color2_hex), dtype=np.float32)
        
        if direction == "horizontal":
            for x in range(width):
                t = x / width
                color = color1 * (1 - t) + color2 * t
                frame[:, x] = color.astype(np.uint8)
        elif direction == "vertical":
            for y in range(height):
                t = y / height
                color = color1 * (1 - t) + color2 * t
                frame[y, :] = color.astype(np.uint8)
        elif direction == "diagonal":
            for y in range(height):
                for x in range(width):
                    t = (x / width + y / height) / 2
                    color = color1 * (1 - t) + color2 * t
                    frame[y, x] = color.astype(np.uint8)
        
        return frame


class BarsLayer(Layer):
    """
    Epic 04.B6: Bars layer - renders horizontal or vertical bars.
    """
    
    def __init__(self):
        super().__init__("bars", "Bars")
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "orientation": {"type": "choice", "default": "horizontal", "choices": ["horizontal", "vertical"]},
            "bar_count": {"type": "int", "default": 4, "min": 1, "max": 20},
            "color": {"type": "color", "default": "#FFFFFF"},
        }
    
    def render_frame(
        self,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT
    ) -> np.ndarray:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        orientation = params.get("orientation", "horizontal")
        bar_count = params.get("bar_count", 4)
        color_hex = params.get("color", "#FFFFFF")
        
        color = np.array(WaveLayer._parse_color(color_hex), dtype=np.uint8)
        
        if orientation == "horizontal":
            bar_height = height // bar_count
            for i in range(bar_count):
                start_y = i * bar_height
                end_y = start_y + bar_height
                frame[start_y:end_y, :] = color
        else:  # vertical
            bar_width = width // bar_count
            for i in range(bar_count):
                start_x = i * bar_width
                end_x = start_x + bar_width
                frame[:, start_x:end_x] = color
        
        return frame


class RingsLayer(Layer):
    """
    Epic 04.B7: Rings layer - renders concentric rings or expanding pulse.
    """
    
    def __init__(self):
        super().__init__("rings", "Rings")
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "center_x": {"type": "int", "default": 50, "min": 0, "max": 100},
            "center_y": {"type": "int", "default": 25, "min": 0, "max": 50},
            "ring_spacing": {"type": "int", "default": 5, "min": 1, "max": 20},
            "ring_width": {"type": "int", "default": 2, "min": 1, "max": 10},
            "color": {"type": "color", "default": "#FFFFFF"},
        }
    
    def render_frame(
        self,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT
    ) -> np.ndarray:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        center_x = params.get("center_x", 50)
        center_y = params.get("center_y", 25)
        ring_spacing = params.get("ring_spacing", 5)
        ring_width = params.get("ring_width", 2)
        color_hex = params.get("color", "#FFFFFF")
        
        color = np.array(WaveLayer._parse_color(color_hex), dtype=np.uint8)
        
        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                ring_index = int(dist / ring_spacing)
                distance_in_ring = (dist % ring_spacing)
                
                if distance_in_ring < ring_width:
                    frame[y, x] = color
        
        return frame


class BeatFlashLayer(Layer):
    """
    Epic 04.B8: Beat flash layer - flashes on beat onsets.
    """
    
    def __init__(self):
        super().__init__("beat_flash", "Beat Flash")
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "color": {"type": "color", "default": "#FFFFFF"},
            "decay": {"type": "float", "default": 0.9, "min": 0.5, "max": 1.0},
        }
    
    def render_frame(
        self,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT
    ) -> np.ndarray:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        color_hex = params.get("color", "#FFFFFF")
        decay = params.get("decay", 0.9)
        
        base_color = WaveLayer._parse_color(color_hex)
        
        # Flash intensity based on beat progress
        if context.onset_detected:
            intensity = 255
        else:
            intensity = int(255 * context.beat_progress * decay)
        
        if intensity > 0:
            color = tuple(c * intensity // 255 for c in base_color)
            frame[:, :] = color
        
        return frame


class ScannerLayer(Layer):
    """
    Epic 04.B9: Scanner layer - sweep/scanner effect.
    """
    
    def __init__(self):
        super().__init__("scanner", "Scanner")
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "sweep_speed": {"type": "float", "default": 1.0, "min": 0.1, "max": 5.0},
            "sweep_width": {"type": "int", "default": 10, "min": 1, "max": 30},
            "color": {"type": "color", "default": "#FFFFFF"},
        }
    
    def render_frame(
        self,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT
    ) -> np.ndarray:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        sweep_speed = params.get("sweep_speed", 1.0)
        sweep_width = params.get("sweep_width", 10)
        color_hex = params.get("color", "#FFFFFF")
        
        base_color = WaveLayer._parse_color(color_hex)
        
        # Calculate scanner position
        scanner_pos = (context.frame_time * sweep_speed * width) % width
        
        for y in range(height):
            for x in range(width):
                dist = abs(x - scanner_pos)
                if dist < sweep_width:
                    intensity = int(255 * (1.0 - dist / sweep_width))
                    frame[y, x] = tuple(c * intensity // 255 for c in base_color)
        
        return frame


class BlendMode(ABC):
    """Base class for blend operations."""
    
    @staticmethod
    @abstractmethod
    def blend(bottom: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
        """
        Blend top layer onto bottom layer.
        
        Args:
            bottom: Background layer (height, width, 3)
            top: Top layer (height, width, 3)
            opacity: Top layer opacity (0-1)
        
        Returns:
            Blended result (height, width, 3)
        """
        pass


class AlphaBlend(BlendMode):
    """Epic 04.B11: Alpha blend mode."""
    
    @staticmethod
    def blend(bottom: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
        top = (top.astype(np.float32) * opacity).astype(np.uint8)
        return ((bottom.astype(np.float32) * (1 - opacity) + top.astype(np.float32) * opacity)).astype(np.uint8)


class MaxBlend(BlendMode):
    """Epic 04.B11: Max blend mode - takes maximum of each channel."""
    
    @staticmethod
    def blend(bottom: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
        top_scaled = (top.astype(np.float32) * opacity).astype(np.uint8)
        return np.maximum(bottom, top_scaled)


class AddBlend(BlendMode):
    """Epic 04.B11: Add blend mode - additive blending."""
    
    @staticmethod
    def blend(bottom: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
        top_scaled = (top.astype(np.float32) * opacity).astype(np.uint8)
        result = bottom.astype(np.float32) + top_scaled.astype(np.float32)
        return np.clip(result, 0, 255).astype(np.uint8)


class MultiplyBlend(BlendMode):
    """Epic 04.B11: Multiply blend mode."""
    
    @staticmethod
    def blend(bottom: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
        result = (bottom.astype(np.float32) / 255.0) * (top.astype(np.float32) / 255.0 * opacity)
        return (result * 255).astype(np.uint8)


class ScreenBlend(BlendMode):
    """Epic 04.B11: Screen blend mode."""
    
    @staticmethod
    def blend(bottom: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
        bottom_norm = bottom.astype(np.float32) / 255.0
        top_norm = (top.astype(np.float32) / 255.0) * opacity
        result = 1.0 - (1.0 - bottom_norm) * (1.0 - top_norm)
        return (result * 255).astype(np.uint8)


class DifferenceBlend(BlendMode):
    """Epic 04.B11: Difference blend mode."""
    
    @staticmethod
    def blend(bottom: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
        top_scaled = (top.astype(np.float32) * opacity).astype(np.uint8)
        return np.abs(bottom.astype(np.int16) - top_scaled.astype(np.int16)).astype(np.uint8)


class MaskBlend(BlendMode):
    """Epic 04.B11: Mask blend mode - top acts as mask."""
    
    @staticmethod
    def blend(bottom: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
        # Use grayscale value of top as mask
        mask = np.mean(top, axis=2, keepdims=True) / 255.0 * opacity
        return (bottom.astype(np.float32) * mask).astype(np.uint8)


class ReplaceBlend(BlendMode):
    """Epic 04.B11: Replace blend mode - completely replaces bottom."""
    
    @staticmethod
    def blend(bottom: np.ndarray, top: np.ndarray, opacity: float = 1.0) -> np.ndarray:
        if opacity == 1.0:
            return top.copy()
        return ((top.astype(np.float32) * opacity + bottom.astype(np.float32) * (1 - opacity))).astype(np.uint8)


# Blend mode registry
BLEND_MODES = {
    "alpha": AlphaBlend,
    "max": MaxBlend,
    "add": AddBlend,
    "multiply": MultiplyBlend,
    "screen": ScreenBlend,
    "difference": DifferenceBlend,
    "mask": MaskBlend,
    "replace": ReplaceBlend,
}


class LayerRegistry:
    """
    Epic 04.B1, B12: Layer registry for managing and composing layers.
    
    Provides registry-based layer loading and composition with deterministic seeded execution.
    """
    
    def __init__(self):
        self.layers: Dict[str, Layer] = {}
        self._register_builtin_layers()
    
    def _register_builtin_layers(self) -> None:
        """Register all built-in layer implementations."""
        builtin_layers = [
            WaveLayer(),
            RadialPulseLayer(),
            SolidFieldLayer(),
            GradientFieldLayer(),
            BarsLayer(),
            RingsLayer(),
            BeatFlashLayer(),
            ScannerLayer(),
        ]
        for layer in builtin_layers:
            self.layers[layer.layer_id] = layer
    
    def get_layer(self, layer_id: str) -> Optional[Layer]:
        """Get a layer by ID."""
        return self.layers.get(layer_id)
    
    def register_layer(self, layer: Layer) -> None:
        """Register a custom layer."""
        self.layers[layer.layer_id] = layer
    
    def list_layers(self) -> List[str]:
        """List all registered layer IDs."""
        return list(self.layers.keys())
    
    def render_layer_frame(
        self,
        layer_id: str,
        context: RenderContext,
        params: Dict[str, Any],
        width: int = CANVAS_WIDTH,
        height: int = CANVAS_HEIGHT
    ) -> Optional[np.ndarray]:
        """
        Render a frame from a layer.
        
        Epic 04.B1: Deterministic seeded execution.
        """
        layer = self.get_layer(layer_id)
        if not layer:
            return None
        return layer.render_frame(context, params, width, height)
