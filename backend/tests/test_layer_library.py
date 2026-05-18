import numpy as np
import pytest

from analysis.schema import AnalysisSignals
from shaders.blend import blend
from shaders.registry import get, list_layers
from shaders.types import LayerContext


def _signals() -> AnalysisSignals:
    return AnalysisSignals(
        beat_phase=0.0, bar_phase=0.0, nearest_beat_distance=0.0,
        bass=0.5, mid=0.5, high=0.5, energy=0.5,
    )


def _ctx(frame: int = 0, params: dict | None = None) -> LayerContext:
    return LayerContext(
        frame=frame, fps=30.0, seed=42, params=params or {},
        signals=_signals(),
    )


def test_registry_has_bouncing_ball():
    cls = get("bouncing_ball")
    assert cls is not None


def test_registry_lists_all_layers():
    ids = {m.layer_id for m in list_layers()}
    assert "bouncing_ball" in ids
    assert "solid" in ids
    assert "gradient" in ids
    assert "wave" in ids
    assert "beat_flash" in ids


def test_bouncing_ball_frame0_at_start():
    cls = get("bouncing_ball")
    layer = cls()
    ctx = _ctx(0, {"start_x": 97, "start_y": 47, "velocity_x": 1, "velocity_y": 1})
    frame = layer.render(ctx)
    assert frame[47, 97, 3] == 255  # pixel is lit


def test_bouncing_ball_frame2_at_corner():
    cls = get("bouncing_ball")
    layer = cls()
    ctx = _ctx(2, {"start_x": 97, "start_y": 47, "velocity_x": 1, "velocity_y": 1})
    frame = layer.render(ctx)
    assert frame[49, 99, 3] == 255  # bottom-right corner


def test_bouncing_ball_frame3_reflected():
    cls = get("bouncing_ball")
    layer = cls()
    ctx = _ctx(3, {"start_x": 97, "start_y": 47, "velocity_x": 1, "velocity_y": 1})
    frame = layer.render(ctx)
    assert frame[48, 98, 3] == 255  # reflected


def test_bouncing_ball_is_deterministic():
    cls = get("bouncing_ball")
    p = {"start_x": 10, "start_y": 10, "velocity_x": 1, "velocity_y": 1}
    f1 = cls().render(_ctx(10, p))
    f2 = cls().render(_ctx(10, p))
    assert np.array_equal(f1, f2)


def test_solid_fills_canvas():
    cls = get("solid")
    frame = cls().render(_ctx(0, {"color": "#ff0000"}))
    assert frame[0, 0, 0] == 255   # R channel
    assert frame[0, 0, 1] == 0     # G channel
    assert np.all(frame[:, :, 3] == 255)  # fully opaque


def test_blend_add_clamps():
    a = np.full((50, 100, 4), 200, dtype=np.uint8)
    b = np.full((50, 100, 4), 200, dtype=np.uint8)
    result = blend(a, b, mode="add")
    assert result.max() == 255


def test_blend_alpha_transparent_over():
    base = np.full((50, 100, 4), 100, dtype=np.uint8)
    over = np.zeros((50, 100, 4), dtype=np.uint8)
    result = blend(base, over, mode="alpha")
    assert np.array_equal(result, base)


def test_blend_rejects_unknown_mode():
    a = np.zeros((50, 100, 4), dtype=np.uint8)
    with pytest.raises(ValueError):
        blend(a, a, mode="dissolve")
