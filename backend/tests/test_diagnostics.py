"""
Tests for Epic 12: Render Diagnostics
"""

import pytest
import sys
from pathlib import Path
import numpy as np

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.diagnostics import (
    DiagnosticsAnalyzer,
    DiagnosticsSummary,
    VarietyMetrics,
)


class TestDiagnosticsAnalyzer:
    """Tests for render diagnostics analysis."""
    
    def test_analyze_blank_frames(self):
        """
        Epic 12.V1: Catch obviously blank renders.
        """
        analyzer = DiagnosticsAnalyzer()
        
        # Create mostly blank frames
        frames = [np.zeros((100, 50, 3), dtype=np.uint8) for _ in range(10)]
        frames.append(np.ones((100, 50, 3), dtype=np.uint8) * 255)  # One bright frame
        
        summary = analyzer.analyze_frames(frames)
        
        assert summary.blank_frame_count >= 8
        assert summary.brightness_avg < 0.2
    
    def test_analyze_static_render(self):
        """
        Epic 12.V2: Catch accidentally static renders.
        """
        analyzer = DiagnosticsAnalyzer()
        
        # Create identical frames (completely static)
        frame = np.ones((100, 50, 3), dtype=np.uint8) * 128
        frames = [frame for _ in range(30)]
        
        summary = analyzer.analyze_frames(frames)
        variety = analyzer.analyze_variety(summary)
        
        assert summary.frame_delta_avg < 0.01
        assert variety.is_static
        assert "static" in " ".join(variety.warnings).lower()
    
    def test_analyze_varied_render(self):
        """Good renders should have measurable variation."""
        analyzer = DiagnosticsAnalyzer()
        
        # Create highly varied frames with larger changes
        frames = []
        for i in range(30):
            # Alternate between very different values
            if i % 2 == 0:
                frame = np.ones((100, 50, 3), dtype=np.uint8) * 50
            else:
                frame = np.ones((100, 50, 3), dtype=np.uint8) * 200
            frames.append(frame)
        
        summary = analyzer.analyze_frames(frames)
        variety = analyzer.analyze_variety(summary)
        
        # Should have decent variation
        assert summary.frame_delta_avg > 0.5
        assert not variety.is_static
    
    def test_generate_contact_sheet(self):
        """Epic 12.B3: Contact sheet generation."""
        analyzer = DiagnosticsAnalyzer()
        
        frames = [np.random.randint(0, 256, (100, 50, 3), dtype=np.uint8) for _ in range(10)]
        
        contact_sheet = analyzer.generate_contact_sheet(frames, grid_size=2)
        
        assert contact_sheet.size == (200, 100)
    
    def test_generate_preview_gif(self):
        """Epic 12.B4: Preview GIF/strip generation."""
        analyzer = DiagnosticsAnalyzer()
        
        frames = [np.random.randint(0, 256, (100, 50, 3), dtype=np.uint8) for _ in range(100)]
        
        preview = analyzer.generate_preview_gif(frames, frame_count=10)
        
        # Frame shape is (height=100, width=50, channels=3), so PIL size is (width=50, height=100)
        assert preview.size == (50, 100)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
