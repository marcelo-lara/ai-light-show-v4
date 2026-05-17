"""
Test Pattern Generation

Epic 11.V1, V2: Generate orientation and ordering test patterns for validation
"""

from typing import Tuple
import numpy as np


class TestPatternGenerator:
    """
    Generates visual test patterns for validating mapping and orientation.
    """
    
    CANVAS_WIDTH = 100
    CANVAS_HEIGHT = 50
    
    @staticmethod
    def orientation_test_pattern() -> np.ndarray:
        """
        Epic 11.V1: Orientation test pattern.
        
        Creates quadrant pattern to validate canvas origin and coordinate system:
        - Top-left: Red (255, 0, 0)
        - Top-right: Green (0, 255, 0)
        - Bottom-left: Blue (0, 0, 255)
        - Bottom-right: Yellow (255, 255, 0)
        
        Returns:
            RGB frame (50, 100, 3)
        """
        frame = np.zeros((50, 100, 3), dtype=np.uint8)
        
        # Top-left quadrant: Red
        frame[0:25, 0:50, 0] = 255  # R
        
        # Top-right quadrant: Green
        frame[0:25, 50:100, 1] = 255  # G
        
        # Bottom-left quadrant: Blue
        frame[25:50, 0:50, 2] = 255  # B
        
        # Bottom-right quadrant: Yellow
        frame[25:50, 50:100, 0] = 255  # R
        frame[25:50, 50:100, 1] = 255  # G
        
        return frame
    
    @staticmethod
    def gradient_left_to_right() -> np.ndarray:
        """
        Left-to-right gradient (black to white).
        
        Used to detect left-right reversal issues.
        
        Returns:
            RGB frame (50, 100, 3)
        """
        frame = np.zeros((50, 100, 3), dtype=np.uint8)
        
        for x in range(100):
            intensity = int((x / 100.0) * 255)
            frame[:, x, :] = intensity
        
        return frame
    
    @staticmethod
    def gradient_top_to_bottom() -> np.ndarray:
        """
        Top-to-bottom gradient (black to white).
        
        Used to detect top-bottom reversal issues.
        
        Returns:
            RGB frame (50, 100, 3)
        """
        frame = np.zeros((50, 100, 3), dtype=np.uint8)
        
        for y in range(50):
            intensity = int((y / 50.0) * 255)
            frame[y, :, :] = intensity
        
        return frame
    
    @staticmethod
    def checkerboard() -> np.ndarray:
        """
        Checkerboard pattern (alternating black/white).
        
        Used to detect irregular pixel ordering.
        
        Returns:
            RGB frame (50, 100, 3)
        """
        frame = np.zeros((50, 100, 3), dtype=np.uint8)
        
        for y in range(50):
            for x in range(100):
                if (x + y) % 2 == 0:
                    frame[y, x, :] = 255
        
        return frame
    
    @staticmethod
    def scanlines() -> np.ndarray:
        """
        Horizontal scanlines pattern.
        
        Used to detect row ordering issues (linear vs serpentine).
        
        Returns:
            RGB frame (50, 100, 3)
        """
        frame = np.zeros((50, 100, 3), dtype=np.uint8)
        
        for y in range(50):
            if y % 2 == 0:
                frame[y, :, :] = 255
        
        return frame
    
    @staticmethod
    def column_pattern() -> np.ndarray:
        """
        Vertical column pattern.
        
        Used to detect column ordering issues.
        
        Returns:
            RGB frame (50, 100, 3)
        """
        frame = np.zeros((50, 100, 3), dtype=np.uint8)
        
        for x in range(100):
            if x % 4 == 0:
                frame[:, x, :] = 255
        
        return frame
    
    @staticmethod
    def diag_gradient() -> np.ndarray:
        """
        Diagonal gradient pattern.
        
        Used to detect complex mapping issues.
        
        Returns:
            RGB frame (50, 100, 3)
        """
        frame = np.zeros((50, 100, 3), dtype=np.uint8)
        
        max_dist = (100 * 100 + 50 * 50) ** 0.5
        
        for y in range(50):
            for x in range(100):
                dist = (x * x + y * y) ** 0.5
                intensity = int((dist / max_dist) * 255)
                frame[y, x, :] = intensity
        
        return frame
    
    @staticmethod
    def linear_sequence() -> np.ndarray:
        """
        Linear pixel sequence pattern (0-254 gradient).
        
        Used to validate exact pixel ordering with visible sequence.
        Maps pixel linear index to brightness (0-254).
        
        Returns:
            RGB frame (50, 100, 3)
        """
        frame = np.zeros((50, 100, 3), dtype=np.uint8)
        
        # Flatten the frame
        frame_flat = frame.reshape(-1, 3)
        
        # Assign intensity based on linear index (0-254 scaled to 5000 pixels)
        for idx in range(5000):
            intensity = int((idx / 5000.0) * 254)
            frame_flat[idx] = intensity
        
        return frame.reshape(50, 100, 3)
    
    @staticmethod
    def serpentine_sequence() -> np.ndarray:
        """
        Serpentine pixel sequence pattern.
        
        Used to validate serpentine (boustrophedon) pixel ordering.
        
        Returns:
            RGB frame (50, 100, 3)
        """
        frame = np.zeros((50, 100, 3), dtype=np.uint8)
        
        idx = 0
        for y in range(50):
            if y % 2 == 0:
                # Even rows: left to right
                for x in range(100):
                    intensity = int((idx / 5000.0) * 254)
                    frame[y, x, :] = intensity
                    idx += 1
            else:
                # Odd rows: right to left (serpentine)
                for x in range(99, -1, -1):
                    intensity = int((idx / 5000.0) * 254)
                    frame[y, x, :] = intensity
                    idx += 1
        
        return frame


class TestPatternAnalyzer:
    """
    Analyzes rendered test patterns to validate mapping correctness.
    """
    
    @staticmethod
    def analyze_orientation(rendered_frame: np.ndarray) -> dict:
        """
        Analyze rendered orientation pattern.
        
        Checks if quadrants have expected colors.
        
        Returns:
            Analysis result with color validation
        """
        h, w = rendered_frame.shape[0:2]
        mid_x = w // 2
        mid_y = h // 2
        
        # Extract quadrant averages
        tl = rendered_frame[0:mid_y, 0:mid_x].mean(axis=(0, 1))
        tr = rendered_frame[0:mid_y, mid_x:].mean(axis=(0, 1))
        bl = rendered_frame[mid_y:, 0:mid_x].mean(axis=(0, 1))
        br = rendered_frame[mid_y:, mid_x:].mean(axis=(0, 1))
        
        # Expected: TL=Red, TR=Green, BL=Blue, BR=Yellow
        results = {
            "top_left_red": tl[0] > 200,
            "top_right_green": tr[1] > 200,
            "bottom_left_blue": bl[2] > 200,
            "bottom_right_yellow": br[0] > 200 and br[1] > 200,
        }
        
        return {
            "is_correct": all(results.values()),
            "quadrants": results,
            "averages": {
                "top_left": tl.tolist(),
                "top_right": tr.tolist(),
                "bottom_left": bl.tolist(),
                "bottom_right": br.tolist(),
            }
        }
    
    @staticmethod
    def analyze_gradient_left_right(rendered_frame: np.ndarray) -> dict:
        """
        Analyze left-right gradient for reversal detection.
        
        Checks if brightness increases left to right.
        """
        # Sample middle row
        middle_row = rendered_frame[rendered_frame.shape[0] // 2, :, :].mean(axis=1)
        
        # Check if monotonically increasing
        diffs = np.diff(middle_row)
        is_increasing = np.sum(diffs > 0) > np.sum(diffs < 0)
        
        return {
            "is_correct": is_increasing,
            "reversed": not is_increasing,
            "avg_intensity_start": float(middle_row[0]),
            "avg_intensity_end": float(middle_row[-1]),
        }
    
    @staticmethod
    def analyze_gradient_top_bottom(rendered_frame: np.ndarray) -> dict:
        """
        Analyze top-bottom gradient for reversal detection.
        
        Checks if brightness increases top to bottom.
        """
        # Sample middle column
        middle_col = rendered_frame[:, rendered_frame.shape[1] // 2, :].mean(axis=1)
        
        # Check if monotonically increasing
        diffs = np.diff(middle_col)
        is_increasing = np.sum(diffs > 0) > np.sum(diffs < 0)
        
        return {
            "is_correct": is_increasing,
            "reversed": not is_increasing,
            "avg_intensity_start": float(middle_col[0]),
            "avg_intensity_end": float(middle_col[-1]),
        }
    
    @staticmethod
    def analyze_checkerboard(rendered_frame: np.ndarray) -> dict:
        """
        Analyze checkerboard pattern for irregular ordering.
        
        Checks if alternating pattern is maintained.
        """
        # Sample pattern - check a 10x10 region
        sample = rendered_frame[0:10, 0:10, :].mean(axis=2)
        
        # Check checkerboard regularity
        regular_count = 0
        for y in range(9):
            for x in range(9):
                if (x + y) % 2 == 0:
                    # Should be bright
                    if sample[y, x] > 128:
                        regular_count += 1
                else:
                    # Should be dark
                    if sample[y, x] < 128:
                        regular_count += 1
        
        regularity = regular_count / 81.0
        
        return {
            "is_correct": regularity > 0.8,
            "regularity_score": regularity,
        }
