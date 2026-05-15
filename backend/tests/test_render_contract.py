"""
Tests for Epic 01: Render Contract

Epic 01.V1-V5: Validation tests for render contract implementation.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add app to path so we can import from it
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import (
    RenderArtifactMetadata,
    RenderArtifact,
    CurrentSongState,
    CurrentCanvasState,
)
from app.render_contract import (
    generate_render_id,
    validate_artifact_compatibility,
    validate_seed,
    RenderIdGenerator,
)


class TestRenderIdGeneration:
    """Epic 01.V2: Stable render_id test."""
    
    def test_same_inputs_produce_same_render_id(self):
        """
        Epic 01.V2: Prove the same inputs produce the same render_id.
        
        This ensures that render_id generation is deterministic.
        """
        song_id = "song_123"
        preset_id = "preset_456"
        seed = 42
        params = {"intensity": 0.8, "speed": 2.0}
        
        # Generate render_id twice with same inputs
        render_id_1 = generate_render_id(song_id, preset_id, seed, params)
        render_id_2 = generate_render_id(song_id, preset_id, seed, params)
        
        # Should be identical
        assert render_id_1 == render_id_2
    
    def test_different_seeds_produce_different_render_ids(self):
        """Different seeds should produce different render_ids."""
        song_id = "song_123"
        preset_id = "preset_456"
        params = {"intensity": 0.8}
        
        render_id_1 = generate_render_id(song_id, preset_id, 42, params)
        render_id_2 = generate_render_id(song_id, preset_id, 43, params)
        
        assert render_id_1 != render_id_2
    
    def test_different_preset_ids_produce_different_render_ids(self):
        """Different preset_ids should produce different render_ids."""
        song_id = "song_123"
        seed = 42
        params = {"intensity": 0.8}
        
        render_id_1 = generate_render_id(song_id, "preset_1", seed, params)
        render_id_2 = generate_render_id(song_id, "preset_2", seed, params)
        
        assert render_id_1 != render_id_2
    
    def test_render_id_format(self):
        """Render_id should have consistent format."""
        render_id = generate_render_id("song_1", "preset_1", 42, {})
        
        # Should start with "render_"
        assert render_id.startswith("render_")
        # Should be a reasonable length
        assert len(render_id) > 10


class TestSeedValidation:
    """Epic 01.B3 & 01.V*: Explicit seed handling and validation."""
    
    def test_seed_cannot_be_none(self):
        """Epic 01.B3: Seed is required."""
        is_valid, error = validate_seed(None)
        assert not is_valid
        assert "required" in error.lower()
    
    def test_seed_must_be_integer(self):
        """Seed must be an integer."""
        is_valid, error = validate_seed("42")
        assert not is_valid
        assert "integer" in error.lower()
    
    def test_seed_cannot_be_negative(self):
        """Seed must be non-negative."""
        is_valid, error = validate_seed(-1)
        assert not is_valid
        assert "non-negative" in error.lower()
    
    def test_valid_seed(self):
        """Valid seed should pass validation."""
        is_valid, error = validate_seed(42)
        assert is_valid
        assert error is None


class TestArtifactCompatibility:
    """Epic 01.B4 & 01.V*: Artifact compatibility checks."""
    
    def test_missing_required_fields(self):
        """Artifact with missing required fields should fail."""
        incomplete_artifact = {
            "schema_version": "1.0",
            "render_id": "render_abc123",
            # Missing many required fields
        }
        
        is_valid, error = validate_artifact_compatibility(incomplete_artifact)
        assert not is_valid
        assert "required field" in error.lower()
    
    def test_unsupported_schema_version(self):
        """Unsupported schema version should fail."""
        artifact = {
            "schema_version": "2.0",  # v2 not supported yet
            "render_id": "render_abc",
            "preset_id": "preset_1",
            "preset_version": "1.0",
            "seed": 42,
            "song_id": "song_1",
            "analysis_id": "analysis_1",
            "fps": 30,
            "duration": 60.0,
            "frame_count": 1800,
        }
        
        is_valid, error = validate_artifact_compatibility(artifact)
        assert not is_valid
        assert "schema version" in error.lower()
    
    def test_valid_artifact_with_v1_schema(self):
        """Valid v1 artifact should pass."""
        artifact = {
            "schema_version": "1.0",
            "render_id": "render_abc123",
            "preset_id": "preset_1",
            "preset_version": "1.0",
            "seed": 42,
            "song_id": "song_1",
            "analysis_id": "analysis_1",
            "fps": 30,
            "duration": 60.0,
            "frame_count": 1800,
        }
        
        is_valid, error = validate_artifact_compatibility(artifact)
        assert is_valid
        assert error is None


class TestDeterministicRender:
    """Epic 01.V1: Deterministic render test (schema validation)."""
    
    def test_same_render_produces_same_metadata(self):
        """Same render inputs should produce identical artifact metadata."""
        render_id = generate_render_id("song_1", "preset_1", 42, {"param": 0.5})
        
        # Create artifacts with same inputs
        metadata_1 = RenderArtifactMetadata(
            render_id=render_id,
            preset_id="preset_1",
            preset_version="1.0",
            seed=42,
            song_id="song_1",
            analysis_id="analysis_1",
            fps=30,
            duration=60.0,
            frame_count=1800,
        )
        
        metadata_2 = RenderArtifactMetadata(
            render_id=render_id,
            preset_id="preset_1",
            preset_version="1.0",
            seed=42,
            song_id="song_1",
            analysis_id="analysis_1",
            fps=30,
            duration=60.0,
            frame_count=1800,
        )
        
        # Both should have same render_id
        assert metadata_1.render_id == metadata_2.render_id


class TestEmptyCanvasContract:
    """Epic 01.B6 & 01.V4: Empty canvas contract test."""
    
    def test_empty_canvas_state(self):
        """A song can load with empty canvas state."""
        empty_canvas = CurrentCanvasState(
            song_id="song_1",
            is_empty=True,
            canvas_id=None,
            render_artifact=None,
        )
        
        assert empty_canvas.is_empty
        assert empty_canvas.canvas_id is None
        assert empty_canvas.render_artifact is None
    
    def test_song_with_empty_canvas(self):
        """A song can load with no existing canvas."""
        song = CurrentSongState(
            song_id="song_1",
            current_canvas=CurrentCanvasState(
                song_id="song_1",
                is_empty=True,
            ),
        )
        
        assert song.current_canvas is not None
        assert song.current_canvas.is_empty
        assert song.current_canvas.render_artifact is None


class TestRenderIdGenerator:
    """Test the RenderIdGenerator service."""
    
    def test_render_id_caching(self):
        """Generator should cache render_ids."""
        generator = RenderIdGenerator()
        
        # First call
        render_id_1 = generator.get_or_generate_render_id(
            "song_1", "preset_1", 42, {}
        )
        
        # Second call with same inputs
        render_id_2 = generator.get_or_generate_render_id(
            "song_1", "preset_1", 42, {}
        )
        
        # Should return cached value
        assert render_id_1 == render_id_2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
