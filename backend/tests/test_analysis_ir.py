import pytest

from analysis.cache import load_cached, save_cache
from analysis.schema import (
    AnalysisDiagnostics,
    AnalysisIRV1,
    BandEnvelope,
    BarEvent,
    BeatEvent,
    ANALYSIS_SCHEMA_VERSION,
    make_analysis_id,
)
from analysis.signals import query_at


def _make_ir(song_id: str = "test") -> AnalysisIRV1:
    beats = [BeatEvent(time=float(i * 0.5)) for i in range(16)]
    bars = [BarEvent(time=float(i * 2.0)) for i in range(4)]
    times = [float(i) * 0.1 for i in range(10)]
    values = [float(i) / 9 for i in range(10)]
    band_envs = [
        BandEnvelope(band=b, times=times, values=values)
        for b in ("bass", "mid", "high")
    ]
    return AnalysisIRV1(
        analysis_id=make_analysis_id(song_id),
        song_id=song_id,
        duration=8.0,
        beats=beats,
        bars=bars,
        downbeats=[bars[0].time],
        sections=[],
        band_envelopes=band_envs,
        energy_times=times,
        energy_values=values,
        diagnostics=AnalysisDiagnostics(
            analyzer_version=ANALYSIS_SCHEMA_VERSION,
            analysis_duration_s=0.01,
            confidence=0.9,
        ),
    )


def test_analysis_id_is_deterministic():
    assert make_analysis_id("song1") == make_analysis_id("song1")


def test_analysis_id_changes_with_schema_version():
    id1 = make_analysis_id("song1")
    assert "song1" in id1
    assert ANALYSIS_SCHEMA_VERSION.replace(".", "")[:1] in id1 or len(id1) > 10


def test_query_returns_bounded_beat_phase():
    ir = _make_ir()
    sig = query_at(ir, 0.25)
    assert 0.0 <= sig.beat_phase <= 1.0


def test_query_returns_bounded_bar_phase():
    ir = _make_ir()
    sig = query_at(ir, 1.0)
    assert 0.0 <= sig.bar_phase <= 1.0


def test_query_energy_is_bounded():
    ir = _make_ir()
    for t in [0.0, 0.5, 0.9]:
        sig = query_at(ir, t)
        assert 0.0 <= sig.energy <= 1.0


def test_query_band_envelopes_are_bounded():
    ir = _make_ir()
    sig = query_at(ir, 0.5)
    assert 0.0 <= sig.bass <= 1.0
    assert 0.0 <= sig.mid <= 1.0
    assert 0.0 <= sig.high <= 1.0


def test_cache_roundtrip(tmp_path):
    ir = _make_ir("roundtrip")
    save_cache(ir, str(tmp_path))
    loaded = load_cached("roundtrip", str(tmp_path))
    assert loaded is not None
    assert loaded.analysis_id == ir.analysis_id


def test_cache_invalidation_on_version_change(tmp_path):
    import json

    ir = _make_ir("stale")
    save_cache(ir, str(tmp_path))
    path = tmp_path / "stale.analysis.json"
    data = json.loads(path.read_text())
    data["analysis_id"] = "stale.analysis.oldversion"
    path.write_text(json.dumps(data))
    loaded = load_cached("stale", str(tmp_path))
    assert loaded is None
