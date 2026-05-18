import pytest

from analysis.schema import AnalysisSignals
from modulation.engine import ModulatorBinding, ModulatorEngine


def _signals(**kwargs) -> AnalysisSignals:
    defaults = dict(
        beat_phase=0.5, bar_phase=0.25, nearest_beat_distance=0.1,
        bass=0.8, mid=0.4, high=0.2, energy=0.6,
    )
    defaults.update(kwargs)
    return AnalysisSignals(**defaults)


def _engine() -> ModulatorEngine:
    return ModulatorEngine()


def test_audio_source_beat_phase():
    e = _engine()
    sig = _signals(beat_phase=0.75)
    val = e.resolve("m", ModulatorBinding(source="beat_phase"), sig, 0.0, 0)
    assert val == pytest.approx(0.75)


def test_audio_source_beat_pulse_is_inverted():
    e = _engine()
    sig = _signals(beat_phase=0.75)
    val = e.resolve("m", ModulatorBinding(source="beat_pulse"), sig, 0.0, 0)
    assert val == pytest.approx(0.25)


def test_lfo_sine_returns_0_to_1():
    e = _engine()
    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        val = e.resolve("m", ModulatorBinding(source="lfo", lfo_freq=1.0), _signals(), t, 0)
        assert 0.0 <= val <= 1.0


def test_seeded_random_is_deterministic():
    e1, e2 = _engine(), _engine()
    b = ModulatorBinding(source="random", random_seed=7)
    sig = _signals()
    assert e1.resolve("m", b, sig, 0.0, 42) == e2.resolve("m", b, sig, 0.0, 42)


def test_scale_op():
    e = _engine()
    b = ModulatorBinding(source="beat_phase", ops=[{"op": "scale", "min": 0.0, "max": 10.0}])
    sig = _signals(beat_phase=0.5)
    assert e.resolve("m", b, sig, 0.0, 0) == pytest.approx(5.0)


def test_clamp_op():
    e = _engine()
    b = ModulatorBinding(source="beat_phase", ops=[{"op": "clamp", "min": 0.4, "max": 0.6}])
    sig = _signals(beat_phase=0.9)
    assert e.resolve("m", b, sig, 0.0, 0) == pytest.approx(0.6)


def test_invert_op():
    e = _engine()
    b = ModulatorBinding(source="beat_phase", ops=[{"op": "invert"}])
    sig = _signals(beat_phase=0.3)
    assert e.resolve("m", b, sig, 0.0, 0) == pytest.approx(0.7)


def test_quantize_op():
    e = _engine()
    b = ModulatorBinding(source="beat_phase", ops=[{"op": "quantize", "steps": 4}])
    sig = _signals(beat_phase=0.6)
    result = e.resolve("m", b, sig, 0.0, 0)
    assert result in [0.0, 0.25, 0.5, 0.75, 1.0]


def test_smooth_op_lags_toward_target():
    e = _engine()
    b = ModulatorBinding(source="beat_phase", ops=[{"op": "smooth", "alpha": 0.5, "key": "x"}])
    # First call: state initialises to 0.0, then smooths toward 0.0 → stays 0.0
    sig0 = _signals(beat_phase=0.0)
    e.resolve("m", b, sig0, 0.0, 0)
    # Second call with target=1.0: should be partway between prev(0.0) and 1.0
    sig1 = _signals(beat_phase=1.0)
    v = e.resolve("m", b, sig1, 0.0, 0)
    assert 0.0 < v < 1.0  # lagging toward target


def test_ops_apply_in_order():
    e = _engine()
    b = ModulatorBinding(
        source="beat_phase",
        ops=[{"op": "scale", "min": 0, "max": 2}, {"op": "clamp", "min": 0, "max": 1}],
    )
    sig = _signals(beat_phase=0.9)
    val = e.resolve("m", b, sig, 0.0, 0)
    assert val == pytest.approx(1.0)


def test_resolve_all_returns_dict():
    e = _engine()
    bindings = {
        "a": ModulatorBinding(source="beat_phase"),
        "b": ModulatorBinding(source="energy"),
    }
    result = e.resolve_all(bindings, _signals(), 0.0, 0)
    assert "a" in result and "b" in result
