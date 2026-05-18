import numpy as np
import pytest

from diagnostics.reporter import DiagnosticWarning, analyze_frame, analyze_sequence


def _blank() -> np.ndarray:
    return np.zeros((50, 100, 4), dtype=np.uint8)


def _bright() -> np.ndarray:
    return np.full((50, 100, 4), 200, dtype=np.uint8)


def test_blank_frame_warns():
    result = analyze_frame(_blank())
    assert DiagnosticWarning.BLANK_FRAME in result["warnings"]


def test_bright_frame_no_blank_warning():
    result = analyze_frame(_bright())
    assert DiagnosticWarning.BLANK_FRAME not in result["warnings"]


def test_brightness_value_range():
    result = analyze_frame(_bright())
    assert 0.0 < result["brightness"] <= 1.0


def test_static_sequence_warns():
    frames = [_bright()] * 10
    result = analyze_sequence(frames)
    assert DiagnosticWarning.STATIC_RENDER in result["warnings"]


def test_changing_sequence_no_static_warning():
    frames = [np.full((50, 100, 4), v, dtype=np.uint8) for v in range(0, 255, 25)]
    result = analyze_sequence(frames)
    assert DiagnosticWarning.STATIC_RENDER not in result["warnings"]


def test_low_variety_constant_brightness():
    frames = [np.full((50, 100, 4), 100, dtype=np.uint8) for _ in range(5)]
    result = analyze_sequence(frames)
    assert DiagnosticWarning.LOW_VARIETY in result["warnings"]


def test_empty_sequence_warns_blank():
    result = analyze_sequence([])
    assert DiagnosticWarning.BLANK_FRAME in result["warnings"]


def test_sequence_returns_frame_count():
    frames = [_bright() for _ in range(12)]
    result = analyze_sequence(frames)
    assert result["frame_count"] == 12
