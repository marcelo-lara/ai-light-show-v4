"""
Phase 02 Tests: Musical Analysis IR

Epic 03: Analysis IR
Covers cache invalidation (V1), timestamp query (V2), and signal sanity (V3).
"""

import pytest
from typing import List

from app.analysis_ir import (
    ANALYSIS_SCHEMA_VERSION,
    AnalysisCache,
    AnalysisDiagnostics,
    AnalysisIR,
    AnalysisTimestampQuery,
    BandEnvelope,
    SectionCandidate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_analysis(
    analysis_id: str = "test_song_analysis",
    song_id: str = "test_song",
    duration: float = 4.0,
    fps: float = 10.0,
) -> AnalysisIR:
    """Build a minimal but complete AnalysisIR for testing."""
    n_frames = int(duration * fps)
    beat_interval = 0.5  # 120 BPM
    beat_times = [i * beat_interval for i in range(int(duration / beat_interval))]

    beat_phase: List[float] = []
    nearest_beat_distance: List[float] = []
    bar_phase: List[float] = []
    global_energy: List[float] = []

    bar_interval = beat_interval * 4
    bar_times = [i * bar_interval for i in range(int(duration / bar_interval) + 1)]

    for f in range(n_frames):
        t = f / fps
        # Beat phase: progress within current beat
        pos_in_beat = t % beat_interval
        bp = pos_in_beat / beat_interval
        beat_phase.append(round(bp, 6))

        # Nearest beat distance (signed)
        nearest = min(abs(t - bt) for bt in beat_times) if beat_times else 0.0
        nearest_beat_distance.append(round(nearest, 6))

        # Bar phase
        pos_in_bar = t % bar_interval
        bar_phase.append(round(pos_in_bar / bar_interval, 6))

        # Global energy: simple sinusoidal proxy
        import math
        ge = 0.5 + 0.5 * math.sin(2 * math.pi * t / beat_interval)
        global_energy.append(round(min(1.0, max(0.0, ge)), 6))

    band_envelopes = [
        BandEnvelope(
            band_index=i,
            values=[round(min(1.0, max(0.0, (f / n_frames + i * 0.1) % 1.0)), 6) for f in range(n_frames)],
            sample_rate_fps=fps,
        )
        for i in range(4)
    ]

    structure_candidates = [
        SectionCandidate(start_time=0.0, end_time=2.0, type="phrase", confidence=0.9),
        SectionCandidate(start_time=2.0, end_time=4.0, type="phrase", confidence=0.85),
        SectionCandidate(start_time=0.0, end_time=4.0, type="section", confidence=0.7),
    ]

    diagnostics = AnalysisDiagnostics(
        analyzer_version="test-1.0",
        beat_confidence=0.92,
        source_metadata={"source": "synthetic"},
        debug_stats={"n_frames": n_frames},
    )

    return AnalysisIR(
        analysis_id=analysis_id,
        song_id=song_id,
        duration=duration,
        fps=fps,
        beat_times=beat_times,
        beat_phase=beat_phase,
        nearest_beat_distance=nearest_beat_distance,
        bar_times=bar_times,
        bar_phase=bar_phase,
        band_envelopes=band_envelopes,
        global_energy=global_energy,
        structure_candidates=structure_candidates,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# Epic 03.B1: Schema version
# ---------------------------------------------------------------------------


class TestAnalysisIRSchema:
    """Prove the schema version field exists and is stable (Epic 03.B1)."""

    def test_schema_version_constant_is_string(self):
        assert isinstance(ANALYSIS_SCHEMA_VERSION, str)
        assert len(ANALYSIS_SCHEMA_VERSION) > 0

    def test_analysis_ir_carries_schema_version(self):
        ir = _make_analysis()
        assert ir.schema_version == ANALYSIS_SCHEMA_VERSION

    def test_analysis_ir_required_fields(self):
        ir = _make_analysis("id1", "song1", duration=2.0)
        assert ir.analysis_id == "id1"
        assert ir.song_id == "song1"
        assert ir.duration == 2.0

    def test_diagnostics_schema_version_matches(self):
        ir = _make_analysis()
        assert ir.diagnostics is not None
        assert ir.diagnostics.analysis_schema_version == ANALYSIS_SCHEMA_VERSION


# ---------------------------------------------------------------------------
# Epic 03.V1: Cache invalidation
# ---------------------------------------------------------------------------


class TestAnalysisCache:
    """Epic 03.V1: Prove schema changes invalidate cached analysis."""

    def test_cache_stores_and_retrieves(self):
        cache = AnalysisCache()
        ir = _make_analysis("song_a")
        cache.put(ir)
        result = cache.get("song_a")
        assert result is not None
        assert result.analysis_id == "song_a"

    def test_cache_miss_returns_none(self):
        cache = AnalysisCache()
        assert cache.get("nonexistent") is None

    def test_schema_version_mismatch_evicts_entry(self):
        """Simulate a schema bump by patching the stored entry's version."""
        cache = AnalysisCache()
        ir = _make_analysis("song_b")
        cache.put(ir)

        # Manually corrupt the stored version to simulate an old-schema entry
        key = f"{ANALYSIS_SCHEMA_VERSION}:song_b"
        cache._store[key] = ir.model_copy(update={"schema_version": "0.0-old"})

        result = cache.get("song_b")
        assert result is None, "Stale schema entry should be evicted"

    def test_invalidate_removes_entry(self):
        cache = AnalysisCache()
        ir = _make_analysis("song_c")
        cache.put(ir)
        cache.invalidate("song_c")
        assert cache.get("song_c") is None

    def test_clear_removes_all_entries(self):
        cache = AnalysisCache()
        for i in range(3):
            cache.put(_make_analysis(f"song_{i}"))
        cache.clear()
        assert cache.list_ids() == []

    def test_list_ids_returns_analysis_ids(self):
        cache = AnalysisCache()
        cache.put(_make_analysis("alpha"))
        cache.put(_make_analysis("beta"))
        ids = cache.list_ids()
        assert "alpha" in ids
        assert "beta" in ids


# ---------------------------------------------------------------------------
# Epic 03.V2: Timestamp query
# ---------------------------------------------------------------------------


class TestAnalysisTimestampQuery:
    """Epic 03.V2: Prove beat_phase, bar_phase, and nearest_beat fields are available."""

    def setup_method(self):
        self.ir = _make_analysis(duration=4.0, fps=10.0)
        self.query = AnalysisTimestampQuery(self.ir)

    def test_at_time_returns_beat_phase(self):
        result = self.query.at_time(0.0)
        assert "beat_phase" in result
        assert 0.0 <= result["beat_phase"] <= 1.0

    def test_at_time_returns_bar_phase(self):
        result = self.query.at_time(0.0)
        assert "bar_phase" in result
        assert 0.0 <= result["bar_phase"] <= 1.0

    def test_at_time_returns_nearest_beat_distance(self):
        result = self.query.at_time(0.0)
        assert "nearest_beat_distance" in result
        assert result["nearest_beat_distance"] >= 0.0

    def test_at_time_returns_global_energy(self):
        result = self.query.at_time(1.0)
        assert "global_energy" in result
        assert 0.0 <= result["global_energy"] <= 1.0

    def test_at_time_returns_fft_bands(self):
        result = self.query.at_time(0.5)
        assert "fft_bands" in result
        assert isinstance(result["fft_bands"], list)
        assert len(result["fft_bands"]) == len(self.ir.band_envelopes)

    def test_at_time_returns_frame_time(self):
        result = self.query.at_time(1.5)
        assert result["frame_time"] == pytest.approx(1.5)

    def test_all_signals_available_at_render_time(self):
        """All required render-time signals present for any valid timestamp."""
        required_keys = {
            "beat_phase", "bar_phase", "nearest_beat_distance",
            "global_energy", "fft_bands", "frame_time",
        }
        for t in [0.0, 0.5, 1.0, 2.0, 3.9]:
            result = self.query.at_time(t)
            assert required_keys <= set(result.keys()), f"Missing keys at t={t}"

    def test_out_of_bounds_time_clamps_gracefully(self):
        """Times beyond duration should clamp to last frame, not raise."""
        result = self.query.at_time(999.0)
        assert 0.0 <= result["beat_phase"] <= 1.0


# ---------------------------------------------------------------------------
# Epic 03.V3: Signal sanity
# ---------------------------------------------------------------------------


class TestAnalysisSignalSanity:
    """Epic 03.V3: Verify signals stay normalised and bounded."""

    def setup_method(self):
        self.ir = _make_analysis(duration=4.0, fps=30.0)

    def test_beat_phase_normalised(self):
        for v in self.ir.beat_phase:
            assert 0.0 <= v <= 1.0, f"beat_phase out of range: {v}"

    def test_bar_phase_normalised(self):
        for v in self.ir.bar_phase:
            assert 0.0 <= v <= 1.0, f"bar_phase out of range: {v}"

    def test_global_energy_normalised(self):
        for v in self.ir.global_energy:
            assert 0.0 <= v <= 1.0, f"global_energy out of range: {v}"

    def test_band_envelopes_normalised(self):
        for env in self.ir.band_envelopes:
            for v in env.values:
                assert 0.0 <= v <= 1.0, f"band_envelope[{env.band_index}] out of range: {v}"

    def test_nearest_beat_distance_non_negative(self):
        for v in self.ir.nearest_beat_distance:
            assert v >= 0.0, f"nearest_beat_distance is negative: {v}"

    def test_beat_times_ordered(self):
        times = self.ir.beat_times
        for i in range(1, len(times)):
            assert times[i] >= times[i - 1], "beat_times not monotonically non-decreasing"

    def test_structure_candidates_confidence_bounded(self):
        for cand in self.ir.structure_candidates:
            assert 0.0 <= cand.confidence <= 1.0

    def test_diagnostics_confidence_bounded(self):
        assert self.ir.diagnostics is not None
        assert 0.0 <= self.ir.diagnostics.beat_confidence <= 1.0
