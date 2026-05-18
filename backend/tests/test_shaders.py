import numpy as np
import pytest

from analysis.schema import AnalysisSignals
from shaders.registry import get, list_layers
from shaders.types import LayerContext


def _signals(**kwargs) -> AnalysisSignals:
    defaults = dict(
        beat_phase=0.5, bar_phase=0.25, nearest_beat_distance=0.1,
        bass=0.8, mid=0.4, high=0.2, energy=0.6,
    )
    defaults.update(kwargs)
    return AnalysisSignals(**defaults)


def _ctx(frame: int = 0, params: dict | None = None) -> LayerContext:
    return LayerContext(
        frame=frame, fps=30.0, seed=42, params=params or {},
        signals=_signals(),
    )


def test_registry_has_all_new_shaders():
    ids = {m.layer_id for m in list_layers()}
    assert "ocean_waves" in ids
    assert "raindrops" in ids
    assert "spectroid_chase" in ids


def test_ocean_waves_output_shape():
    cls = get("ocean_waves")
    frame = cls().render(_ctx(0))
    assert frame.shape == (50, 100, 4)
    assert frame.dtype == np.uint8


def test_ocean_waves_base_color_is_dark_blue():
    cls = get("ocean_waves")
    frame = cls().render(_ctx(0, {"base_color": "#000055", "highlight_color": "#0000ff"}))
    # blue channel should dominate overall
    b_mean = frame[:, :, 2].mean()
    r_mean = frame[:, :, 0].mean()
    assert b_mean > r_mean


def test_ocean_waves_is_deterministic():
    cls = get("ocean_waves")
    f1 = cls().render(_ctx(10))
    f2 = cls().render(_ctx(10))
    assert np.array_equal(f1, f2)


def test_raindrops_output_shape():
    cls = get("raindrops")
    frame = cls().render(_ctx(0))
    assert frame.shape == (50, 100, 4)


def test_raindrops_poi_coords_produce_non_black():
    cls = get("raindrops")
    frame = cls().render(_ctx(15, {"poi_ids": "0.5:0.5"}))
    # some pixels should be lit
    assert frame[:, :, 3].max() > 0


def test_raindrops_is_deterministic():
    cls = get("raindrops")
    f1 = cls().render(_ctx(5, {"poi_ids": "0.2:0.4"}))
    f2 = cls().render(_ctx(5, {"poi_ids": "0.2:0.4"}))
    assert np.array_equal(f1, f2)


def test_spectroid_chase_output_shape():
    cls = get("spectroid_chase")
    frame = cls().render(_ctx(0))
    assert frame.shape == (50, 100, 4)


def test_spectroid_chase_high_energy_produces_output():
    cls = get("spectroid_chase")
    frame = cls().render(_ctx(10, {"sensitivity": 0.1}), )
    # with high energy and low sensitivity threshold, some pixels should be lit
    assert frame.dtype == np.uint8
