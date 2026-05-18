import pytest

from render.artifact import ArtifactMetaV1, make_render_id
from render.compat import CompatibilityError, check_artifact_compat
from render.seed import SeedError, validate_seed
from session.state import get_state


def _base_meta(**overrides) -> dict:
    return {
        "schema_version": 1,
        "render_id": "abc123",
        "preset_id": "bouncing_ball",
        "preset_version": "1.0.0",
        "seed": 42,
        "params": {},
        "song_id": "test_song",
        "analysis_id": "test_song.analysis",
        "fps": 30.0,
        "duration": 10.0,
        "frame_count": 300,
        **overrides,
    }


def test_render_id_is_stable():
    assert make_render_id("s", "p", 42, {}) == make_render_id("s", "p", 42, {})


def test_render_id_differs_on_different_seed():
    assert make_render_id("s", "p", 42, {}) != make_render_id("s", "p", 43, {})


def test_render_id_differs_on_different_params():
    assert make_render_id("s", "p", 1, {"a": 1}) != make_render_id("s", "p", 1, {"a": 2})


def test_artifact_meta_validates():
    meta = ArtifactMetaV1.model_validate(_base_meta())
    assert meta.schema_version == 1
    assert meta.status.approved is False


def test_compat_check_passes_v1():
    meta = check_artifact_compat(_base_meta())
    assert isinstance(meta, ArtifactMetaV1)


def test_compat_check_rejects_unknown_version():
    with pytest.raises(CompatibilityError):
        check_artifact_compat(_base_meta(schema_version=99))


def test_compat_check_rejects_missing_field():
    raw = _base_meta()
    del raw["render_id"]
    with pytest.raises(CompatibilityError):
        check_artifact_compat(raw)


def test_seed_accepts_int():
    assert validate_seed(42) == 42


def test_seed_rejects_none():
    with pytest.raises(SeedError):
        validate_seed(None)


def test_seed_rejects_non_int():
    with pytest.raises(SeedError):
        validate_seed("42")  # type: ignore[arg-type]


def test_empty_canvas_on_new_session():
    state = get_state()
    assert state.current_song is None
    assert state.current_canvas is None
    assert state.available_canvases == []


def test_playback_initial_state():
    state = get_state()
    assert state.playback.transport == "stopped"
    assert state.playback.position == 0.0
