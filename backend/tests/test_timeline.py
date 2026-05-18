import numpy as np
import pytest

from analysis.schema import AnalysisIRV1, BeatEvent, SectionCandidate, AnalysisDiagnostics
from timeline.director import build_from_sections
from timeline.schema import TimelineV1
from timeline.transitions import apply_transition, crossfade, hard_cut, beat_flash_cut


def _diag(**kwargs) -> AnalysisDiagnostics:
    return AnalysisDiagnostics(
        analyzer_version="test", analysis_duration_s=0.1, confidence=0.9, **kwargs
    )


def _ir_with_sections() -> AnalysisIRV1:
    return AnalysisIRV1(
        song_id="test",
        analysis_id="abc123",
        duration=120.0,
        beats=[BeatEvent(time=t, confidence=1.0) for t in [0.0, 0.47, 0.94]],
        bars=[],
        downbeats=[],
        sections=[
            SectionCandidate(start=0.0, end=30.0, label="verse", confidence=0.9),
            SectionCandidate(start=30.0, end=60.0, label="chorus", confidence=0.9),
            SectionCandidate(start=60.0, end=90.0, label="verse", confidence=0.9),
            SectionCandidate(start=90.0, end=120.0, label="outro", confidence=0.9),
        ],
        band_envelopes=[],
        energy_times=[],
        energy_values=[],
        diagnostics=_diag(onset_count=0, beat_count=3, section_count=4),
    )


def _ir_no_sections() -> AnalysisIRV1:
    return AnalysisIRV1(
        song_id="test",
        analysis_id="abc123",
        duration=60.0,
        beats=[BeatEvent(time=i * 0.5, confidence=1.0) for i in range(40)],
        bars=[],
        downbeats=[],
        sections=[],
        band_envelopes=[],
        energy_times=[],
        energy_values=[],
        diagnostics=_diag(onset_count=0, beat_count=40, section_count=0),
    )


def test_build_from_sections_creates_scenes():
    tl = build_from_sections(_ir_with_sections(), "test_song")
    assert tl.source == "auto_sections"
    assert len(tl.scenes) == 4
    assert tl.scenes[0].start == 0.0
    assert tl.scenes[1].start == 30.0


def test_build_from_sections_boundaries_align_to_sections():
    tl = build_from_sections(_ir_with_sections(), "test_song")
    assert all(s.end <= 120.0 for s in tl.scenes)


def test_build_falls_back_to_beats_when_no_sections():
    tl = build_from_sections(_ir_no_sections(), "test_song")
    assert tl.source == "auto_beats"
    assert len(tl.scenes) >= 1


def test_scene_overrides_do_not_break_structure():
    tl = build_from_sections(_ir_with_sections(), "test_song")
    tl.scenes[0].params["speed"] = 0.5
    assert tl.scenes[0].params["speed"] == 0.5
    assert tl.scenes[1].params == {}


def test_hard_cut_before_half():
    a = np.zeros((50, 100, 4), dtype=np.uint8)
    b = np.full((50, 100, 4), 200, dtype=np.uint8)
    result = hard_cut(a, b, progress=0.3)
    assert np.array_equal(result, a)


def test_hard_cut_after_half():
    a = np.zeros((50, 100, 4), dtype=np.uint8)
    b = np.full((50, 100, 4), 200, dtype=np.uint8)
    result = hard_cut(a, b, progress=0.7)
    assert np.array_equal(result, b)


def test_crossfade_midpoint():
    a = np.full((50, 100, 4), 100, dtype=np.uint8)
    b = np.full((50, 100, 4), 200, dtype=np.uint8)
    result = crossfade(a, b, progress=0.5)
    assert result[0, 0, 0] == 150


def test_crossfade_is_deterministic():
    a = np.full((50, 100, 4), 80, dtype=np.uint8)
    b = np.full((50, 100, 4), 180, dtype=np.uint8)
    r1 = crossfade(a, b, 0.25)
    r2 = crossfade(a, b, 0.25)
    assert np.array_equal(r1, r2)


def test_beat_flash_cut_early_is_white():
    a = np.zeros((50, 100, 4), dtype=np.uint8)
    b = np.zeros((50, 100, 4), dtype=np.uint8)
    result = beat_flash_cut(a, b, progress=0.05)
    assert result[0, 0, 0] == 255  # white flash


def test_apply_transition_unknown_raises():
    a = np.zeros((50, 100, 4), dtype=np.uint8)
    with pytest.raises(ValueError, match="Unknown transition"):
        apply_transition("dissolve", a, a, 0.5)
