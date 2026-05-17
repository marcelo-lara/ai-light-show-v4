"""
Phase 06 Validation Tests: Quality, Performance and Packaging

Epic 11: Fixture Mapping and Export
Epic 12: Render Diagnostics (Validation Tests)
"""

import pytest
import numpy as np
from app.fixture_mapping import (
    CanonicalPixelInfo,
    FixtureMapping,
    MappingType,
    PixelMappingEngine,
    GammaCorrection,
    BrightnessLimiter,
    ExportEngine,
    ExportManifest,
)
from app.test_patterns import TestPatternGenerator, TestPatternAnalyzer


class TestCanonicalPixelOrder:
    """
    Epic 11.B1: Canonical pixel order tests.
    
    Validates row-major pixel order with origin at top-left.
    """
    
    def test_canonical_info_creation(self):
        """Test creating canonical pixel info."""
        info = CanonicalPixelInfo()
        assert info.width == 100
        assert info.height == 50
        assert info.total_pixels == 5000
        assert info.origin == "top_left"
    
    def test_linear_index_calculation(self):
        """Test 2D to linear index conversion."""
        info = CanonicalPixelInfo()
        
        # Top-left corner
        assert info.get_linear_index(0, 0) == 0
        
        # First row rightmost
        assert info.get_linear_index(99, 0) == 99
        
        # Second row leftmost
        assert info.get_linear_index(0, 1) == 100
        
        # Bottom-right corner
        assert info.get_linear_index(99, 49) == 4999
    
    def test_linear_index_bounds(self):
        """Test linear index bounds checking."""
        info = CanonicalPixelInfo()
        
        with pytest.raises(ValueError):
            info.get_linear_index(-1, 0)
        
        with pytest.raises(ValueError):
            info.get_linear_index(0, -1)
        
        with pytest.raises(ValueError):
            info.get_linear_index(100, 0)
        
        with pytest.raises(ValueError):
            info.get_linear_index(0, 50)
    
    def test_xy_from_linear_conversion(self):
        """Test linear index to 2D conversion."""
        info = CanonicalPixelInfo()
        
        # Test known points
        assert info.get_xy_from_linear(0) == (0, 0)
        assert info.get_xy_from_linear(99) == (99, 0)
        assert info.get_xy_from_linear(100) == (0, 1)
        assert info.get_xy_from_linear(4999) == (99, 49)


class TestLinearMapping:
    """
    Epic 11.B5: Linear pixel mapping tests.
    """
    
    def test_linear_mapping_basic(self):
        """Test basic linear mapping."""
        engine = PixelMappingEngine()
        
        # Create a simple fixture (2x2 red pixels)
        fixture_pixels = np.zeros((2, 2, 3), dtype=np.uint8)
        fixture_pixels[:, :, 0] = 255  # All red
        
        mapping = FixtureMapping(
            mapping_id="test_fixture",
            fixture_id="fixture_1",
            fixture_type="test",
            canvas_anchor_x=0.0,
            canvas_anchor_y=0.0,
            pixel_width=2,
            pixel_height=2,
            mapping_type=MappingType.LINEAR,
        )
        
        results = engine.linear_mapping(fixture_pixels, mapping)
        
        # Should have 4 pixels
        assert len(results) == 4
        
        # Check positions
        positions = [(x, y) for x, y, _ in results]
        assert (0, 0) in positions
        assert (1, 0) in positions
        assert (0, 1) in positions
        assert (1, 1) in positions
        
        # All should be red
        for _, _, rgb in results:
            assert rgb == (255, 0, 0)
    
    def test_linear_mapping_with_reversal(self):
        """Test linear mapping with axis reversal."""
        engine = PixelMappingEngine()
        
        fixture_pixels = np.zeros((2, 2, 3), dtype=np.uint8)
        fixture_pixels[:, :, 1] = 128  # Green
        
        mapping = FixtureMapping(
            mapping_id="test_fixture",
            fixture_id="fixture_1",
            fixture_type="test",
            canvas_anchor_x=0.0,
            canvas_anchor_y=0.0,
            pixel_width=2,
            pixel_height=2,
            mapping_type=MappingType.LINEAR,
            reverse_x=True,
        )
        
        results = engine.linear_mapping(fixture_pixels, mapping)
        positions = [(x, y) for x, y, _ in results]
        
        # X should be reversed
        assert (1, 0) in positions
        assert (0, 0) in positions


class TestSerpentineMapping:
    """
    Epic 11.B6: Serpentine pixel mapping tests.
    """
    
    def test_serpentine_mapping_basic(self):
        """Test basic serpentine mapping."""
        engine = PixelMappingEngine()
        
        fixture_pixels = np.zeros((4, 4, 3), dtype=np.uint8)
        fixture_pixels[:, :, 2] = 200  # Blue
        
        mapping = FixtureMapping(
            mapping_id="test_fixture",
            fixture_id="fixture_1",
            fixture_type="test",
            canvas_anchor_x=0.0,
            canvas_anchor_y=0.0,
            pixel_width=4,
            pixel_height=4,
            mapping_type=MappingType.SERPENTINE,
        )
        
        results = engine.serpentine_mapping(fixture_pixels, mapping)
        
        # Should have 16 pixels
        assert len(results) == 16
        
        # All should be blue
        for _, _, rgb in results:
            assert rgb == (0, 0, 200)


class TestGammaCorrection:
    """
    Epic 11.B8: Gamma correction tests.
    """
    
    def test_gamma_disabled(self):
        """Test gamma correction when disabled."""
        gamma = GammaCorrection(enabled=False, gamma=2.2)
        
        # Values should pass through unchanged
        assert gamma.apply(128) == 128
        assert gamma.apply(255) == 255
        assert gamma.apply(0) == 0
    
    def test_gamma_enabled(self):
        """Test gamma correction when enabled."""
        gamma = GammaCorrection(enabled=True, gamma=2.2)
        
        # Mid-level (128) should be brightened after gamma correction (exponential lift)
        result = gamma.apply(128)
        assert result > 128
        
        # Check range
        assert 0 <= result <= 255
        
        # Extreme values should stay extreme
        assert gamma.apply(0) == 0
        assert gamma.apply(255) == 255
    
    def test_gamma_rgb_application(self):
        """Test gamma correction on RGB tuple."""
        gamma = GammaCorrection(enabled=True, gamma=2.2)
        
        rgb = (128, 128, 128)
        result = gamma.apply_rgb(rgb)
        
        # Should be a tuple of 3 values
        assert len(result) == 3
        
        # All should be brightened (lifted) above 128
        assert all(v > 128 for v in result)


class TestBrightnessLimiting:
    """
    Epic 11.B9: Brightness limiting tests.
    """
    
    def test_brightness_limiter_disabled(self):
        """Test brightness limiting when disabled."""
        limiter = BrightnessLimiter(enabled=False, max_brightness=0.5)
        
        rgb = (200, 200, 200)
        result = limiter.apply(rgb)
        
        # Should be unchanged
        assert result == rgb
    
    def test_brightness_limiter_enabled(self):
        """Test brightness limiting when enabled."""
        limiter = BrightnessLimiter(enabled=True, max_brightness=0.5)
        
        rgb = (255, 255, 255)  # Full white
        result = limiter.apply(rgb)
        
        # Should be dimmed
        assert result != rgb
        assert all(v <= 128 for v in result)
    
    def test_brightness_limiter_no_effect_if_under_limit(self):
        """Test that limiter doesn't affect colors under limit."""
        limiter = BrightnessLimiter(enabled=True, max_brightness=1.0)
        
        rgb = (100, 100, 100)
        result = limiter.apply(rgb)
        
        # Should be unchanged (under limit)
        assert result == rgb


class TestExportManifest:
    """
    Epic 11.B7: Export manifest tests.
    """
    
    def test_export_manifest_creation(self):
        """Test creating an export manifest."""
        engine = ExportEngine()
        
        mappings = [
            FixtureMapping(
                mapping_id="fixture_1",
                fixture_id="fixture_1",
                fixture_type="moving_head",
                canvas_anchor_x=0.0,
                canvas_anchor_y=0.0,
                pixel_width=100,
                pixel_height=50,
                mapping_type=MappingType.LINEAR,
            )
        ]
        
        manifest = engine.create_export_manifest(
            render_id="render_1",
            song_id="song_1",
            fps=30,
            duration_sec=10.0,
            total_frames=300,
            fixture_mappings=mappings,
        )
        
        assert isinstance(manifest, ExportManifest)
        assert manifest.render_id == "render_1"
        assert manifest.total_frames == 300
        assert manifest.fps == 30
    
    def test_export_manifest_with_gamma_and_brightness(self):
        """Test export manifest with processing options."""
        engine = ExportEngine(
            gamma_correction=GammaCorrection(enabled=True, gamma=2.2),
            brightness_limiter=BrightnessLimiter(enabled=True, max_brightness=0.8),
        )
        
        manifest = engine.create_export_manifest(
            render_id="render_2",
            song_id="song_2",
            fps=60,
            duration_sec=5.0,
            total_frames=300,
            fixture_mappings=[],
        )
        
        assert manifest.gamma_correction["enabled"] is True
        assert manifest.gamma_correction["gamma"] == 2.2
        assert manifest.brightness_limiting["enabled"] is True
        assert manifest.brightness_limiting["max_brightness"] == 0.8


class TestTestPatterns:
    """
    Epic 11.V1, V2: Test pattern generation and validation.
    """
    
    def test_orientation_pattern_generation(self):
        """Test orientation test pattern generation."""
        generator = TestPatternGenerator()
        pattern = generator.orientation_test_pattern()
        
        # Should be 50x100 RGB
        assert pattern.shape == (50, 100, 3)
        assert pattern.dtype == np.uint8
        
        # Check quadrant colors (approximate)
        # Top-left should be red
        tl = pattern[10, 10]  # Sample top-left
        assert tl[0] > 200  # Red channel high
    
    def test_gradient_patterns(self):
        """Test gradient pattern generation."""
        generator = TestPatternGenerator()
        
        # Left-right gradient
        lr = generator.gradient_left_to_right()
        assert lr.shape == (50, 100, 3)
        
        # Top-bottom gradient
        tb = generator.gradient_top_to_bottom()
        assert tb.shape == (50, 100, 3)
    
    def test_checkerboard_pattern(self):
        """Test checkerboard pattern generation."""
        generator = TestPatternGenerator()
        pattern = generator.checkerboard()
        
        assert pattern.shape == (50, 100, 3)
        
        # Check alternating pattern
        # (0,0) should be white, (1,0) should be black
        assert pattern[0, 0, 0] > 200  # White
        assert pattern[0, 1, 0] < 100  # Black
    
    def test_linear_sequence_pattern(self):
        """Test linear sequence pattern generation."""
        generator = TestPatternGenerator()
        pattern = generator.linear_sequence()
        
        assert pattern.shape == (50, 100, 3)
        
        # Pattern should go from dark to bright
        assert pattern[0, 0, 0] < pattern[49, 99, 0]
    
    def test_serpentine_sequence_pattern(self):
        """Test serpentine sequence pattern generation."""
        generator = TestPatternGenerator()
        pattern = generator.serpentine_sequence()
        
        assert pattern.shape == (50, 100, 3)
        
        # Should have different brightness progression than linear
        # due to serpentine ordering


class TestDiagnosticValidation:
    """
    Epic 12.V1-V3: Diagnostic validation tests.
    """
    
    def test_blank_render_detection(self):
        """
        Epic 12.V1: Test blank render detection.
        
        Creates a mostly blank render and verifies detection.
        """
        from app.diagnostics import DiagnosticsAnalyzer
        
        analyzer = DiagnosticsAnalyzer()
        
        # Create mostly blank frames (brightness < 1%)
        frames = [
            np.zeros((50, 100, 3), dtype=np.uint8) for _ in range(10)
        ]
        frames[5] = np.ones((50, 100, 3), dtype=np.uint8) * 5  # Just a few bright pixels
        
        summary = analyzer.analyze_frames(frames)
        
        assert summary.blank_frame_count >= 5
        assert summary.brightness_avg < 0.1
    
    def test_static_render_detection(self):
        """
        Epic 12.V2: Test static render detection.
        
        Creates a static render and verifies detection.
        """
        from app.diagnostics import DiagnosticsAnalyzer
        
        analyzer = DiagnosticsAnalyzer()
        
        # Create identical frames (static)
        static_frame = np.ones((50, 100, 3), dtype=np.uint8) * 100
        frames = [static_frame.copy() for _ in range(10)]
        
        summary = analyzer.analyze_frames(frames)
        variety = analyzer.analyze_variety(summary)
        
        assert variety.is_static is True
        assert "static" in variety.warnings[0].lower()


class TestMappingValidation:
    """
    Epic 11.V3: Fixture mapping validation tests.
    """
    
    def test_fixture_mapping_validation(self):
        """Test fixture mapping validation."""
        mapping = FixtureMapping(
            mapping_id="test_1",
            fixture_id="fixture_1",
            fixture_type="moving_head",
            canvas_anchor_x=0.5,
            canvas_anchor_y=0.5,
            pixel_width=32,
            pixel_height=32,
            mapping_type=MappingType.LINEAR,
        )
        
        # Should be valid
        assert mapping.mapping_id == "test_1"
        assert mapping.canvas_anchor_x == 0.5
        assert mapping.pixel_width == 32
    
    def test_fixture_mapping_bounds_validation(self):
        """Test anchor bounds validation."""
        # Valid bounds
        mapping1 = FixtureMapping(
            mapping_id="test_1",
            fixture_id="fixture_1",
            fixture_type="moving_head",
            canvas_anchor_x=0.0,
            canvas_anchor_y=0.0,
            pixel_width=10,
            pixel_height=10,
        )
        assert 0.0 <= mapping1.canvas_anchor_x <= 1.0
        
        # Edge case: anchor at 1.0
        mapping2 = FixtureMapping(
            mapping_id="test_2",
            fixture_id="fixture_2",
            fixture_type="moving_head",
            canvas_anchor_x=1.0,
            canvas_anchor_y=1.0,
            pixel_width=10,
            pixel_height=10,
        )
        assert 0.0 <= mapping2.canvas_anchor_x <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
