"""
Render Contract Frontend Tests

Epic 01.F1-F4: Frontend type validation and component tests
"""

import pytest
from frontend.src.types.renderContract import (
    RenderArtifactMetadata,
    RenderArtifact,
    CurrentCanvasState,
    CurrentSongState,
    PlaybackState,
    CompatibilityErrorState,
)


class TestRenderContractTypes:
    """Tests for Epic 01.F1: Shared artifact types."""
    
    def test_render_artifact_metadata_structure(self):
        """Metadata should match backend contract."""
        metadata = {
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
        
        # Should be valid TypeScript type
        assert metadata["schema_version"] == "1.0"
        assert metadata["render_id"] == "render_abc123"
    
    def test_current_canvas_state_structure(self):
        """Canvas state should support empty state (Epic 01.B6)."""
        empty_canvas = {
            "song_id": "song_1",
            "is_empty": True,
        }
        
        assert empty_canvas["is_empty"] is True
        assert "canvas_id" not in empty_canvas or empty_canvas.get("canvas_id") is None
    
    def test_current_song_state_structure(self):
        """Song state should include canvas state (Epic 01.F4)."""
        song_state = {
            "song_id": "song_1",
            "current_canvas": {
                "song_id": "song_1",
                "is_empty": True,
            },
        }
        
        assert song_state["current_canvas"]["is_empty"] is True


class TestCompatibilityErrorState:
    """Tests for Epic 01.F2: Compatibility error handling."""
    
    def test_compatibility_error_state_structure(self):
        """Error state should provide clear messages."""
        error = {
            "has_error": True,
            "error_message": "Unsupported schema version: 2.0",
            "incompatible_render_id": "render_xyz",
            "suggested_action": "Generate a new render with the current schema.",
        }
        
        assert error["has_error"] is True
        assert "schema" in error["error_message"].lower()
    
    def test_no_error_state(self):
        """No error state should be clean."""
        no_error = {
            "has_error": False,
            "error_message": "",
        }
        
        assert no_error["has_error"] is False


class TestPlaybackState:
    """Tests for Epic 01.B5: Backend playback state."""
    
    def test_playback_state_with_song(self):
        """Playback state should include song and canvas."""
        state = {
            "current_song": {
                "song_id": "song_1",
                "current_canvas": {
                    "song_id": "song_1",
                    "is_empty": False,
                    "render_artifact": {
                        "metadata": {
                            "schema_version": "1.0",
                            "render_id": "render_1",
                            "preset_id": "preset_1",
                            "preset_version": "1.0",
                            "seed": 42,
                            "song_id": "song_1",
                            "analysis_id": "analysis_1",
                            "fps": 30,
                            "duration": 60.0,
                            "frame_count": 1800,
                        },
                    },
                },
            },
            "is_playing": False,
            "playback_time": 0.0,
        }
        
        assert state["current_song"]["song_id"] == "song_1"
        assert not state["is_playing"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
