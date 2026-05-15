"""
Canvas rendering and frame display

Epic 02: Canvas frame rendering and display
"""

from typing import List, Optional
import numpy as np
from PIL import Image, ImageDraw


class CanvasRenderer:
    """
    Renders the 100x50 canvas to displayable images.
    """
    
    CANVAS_WIDTH = 100
    CANVAS_HEIGHT = 50
    
    def __init__(self, scale: int = 8):
        """
        Initialize renderer.
        
        Args:
            scale: Scale factor for display (e.g., 8 makes 800x400px for 100x50 canvas)
        """
        self.scale = scale
        self.display_width = self.CANVAS_WIDTH * scale
        self.display_height = self.CANVAS_HEIGHT * scale
    
    def frame_to_image(self, frame: np.ndarray) -> Image.Image:
        """
        Convert a canvas frame to a PIL Image suitable for display.
        
        Args:
            frame: RGB frame array (100x50x3, dtype uint8)
            
        Returns:
            PIL Image scaled by scale factor
        """
        if frame.shape != (self.CANVAS_HEIGHT, self.CANVAS_WIDTH, 3):
            raise ValueError(f"Expected shape ({self.CANVAS_HEIGHT}, {self.CANVAS_WIDTH}, 3)")
        
        # Create PIL image from frame
        img = Image.fromarray(frame, 'RGB')
        
        # Scale up for display using nearest-neighbor (pixel art style)
        if self.scale > 1:
            img = img.resize(
                (self.display_width, self.display_height),
                Image.Resampling.NEAREST
            )
        
        return img
    
    def draw_grid(self, img: Image.Image, grid_color: tuple = (64, 64, 64)) -> Image.Image:
        """
        Draw grid overlay on image to show canvas coordinates.
        
        Args:
            img: PIL Image
            grid_color: RGB tuple for grid lines
            
        Returns:
            Image with grid overlay
        """
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Draw vertical lines
        for x in range(0, self.display_width + 1, self.scale * 10):
            draw.line([(x, 0), (x, self.display_height)], fill=grid_color, width=1)
        
        # Draw horizontal lines
        for y in range(0, self.display_height + 1, self.scale * 10):
            draw.line([(0, y), (self.display_width, y)], fill=grid_color, width=1)
        
        return img
    
    def draw_overlay_markers(
        self,
        img: Image.Image,
        fixtures: List[dict],
        pois: List[dict],
        fixture_color: tuple = (255, 0, 0),
        poi_color: tuple = (0, 255, 0),
    ) -> Image.Image:
        """
        Draw fixture and POI markers on canvas image.
        
        Epic 02.F9-F10: Draw fixtures and POIs as visual overlays.
        
        Args:
            img: PIL Image
            fixtures: List of fixture dicts with canvas_anchor or physical position
            pois: List of POI dicts with canvas_pos
            fixture_color: RGB tuple for fixture markers
            poi_color: RGB tuple for POI markers
            
        Returns:
            Image with overlays drawn
        """
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Draw POIs
        for poi in pois:
            if 'canvas_pos' in poi:
                pos = poi['canvas_pos']
                x = int(pos['x'] * self.scale)
                y = int(pos['y'] * self.scale)
                # Draw as circle
                radius = 5
                draw.ellipse(
                    [(x - radius, y - radius), (x + radius, y + radius)],
                    outline=poi_color,
                    width=2
                )
        
        # Draw fixtures
        for fixture in fixtures:
            canvas_anchor = fixture.get('canvas_anchor')
            if canvas_anchor:
                x = int(canvas_anchor['x'] * self.scale)
                y = int(canvas_anchor['y'] * self.scale)
                # Draw as square
                size = 4
                draw.rectangle(
                    [(x - size, y - size), (x + size, y + size)],
                    fill=fixture_color,
                    outline=fixture_color
                )
        
        return img


class CanvasFrameBuffer:
    """
    Manages frame buffering for playback.
    """
    
    def __init__(self, max_frames: int = 1000):
        self.max_frames = max_frames
        self.frames: List[np.ndarray] = []
        self.current_index = 0
    
    def add_frame(self, frame: np.ndarray):
        """Add a frame to the buffer."""
        if len(self.frames) < self.max_frames:
            self.frames.append(frame)
    
    def get_frame(self, index: int) -> Optional[np.ndarray]:
        """Get a frame by index."""
        if 0 <= index < len(self.frames):
            return self.frames[index]
        return None
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get the current frame."""
        return self.get_frame(self.current_index)
    
    def next_frame(self) -> Optional[np.ndarray]:
        """Advance to next frame."""
        if self.current_index < len(self.frames) - 1:
            self.current_index += 1
        return self.get_current_frame()
    
    def prev_frame(self) -> Optional[np.ndarray]:
        """Go back to previous frame."""
        if self.current_index > 0:
            self.current_index -= 1
        return self.get_current_frame()
    
    def seek(self, index: int) -> Optional[np.ndarray]:
        """Seek to a specific frame."""
        if 0 <= index < len(self.frames):
            self.current_index = index
        return self.get_current_frame()
    
    def clear(self):
        """Clear all frames."""
        self.frames = []
        self.current_index = 0
