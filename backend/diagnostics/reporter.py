from __future__ import annotations

from typing import Any

import numpy as np


class DiagnosticWarning:
    BLANK_FRAME = "blank_frame"
    STATIC_RENDER = "static_render"
    LOW_VARIETY = "low_variety"


def analyze_frame(frame: np.ndarray) -> dict[str, Any]:
    rgb = frame[:, :, :3].astype(np.float32) / 255.0
    brightness = float(rgb.mean())
    avg_color = [float(rgb[:, :, c].mean()) for c in range(3)]
    warnings: list[str] = []
    if brightness < 0.01:
        warnings.append(DiagnosticWarning.BLANK_FRAME)
    return {"brightness": brightness, "avg_color": avg_color, "warnings": warnings}


def analyze_sequence(frames: list[np.ndarray]) -> dict[str, Any]:
    if not frames:
        return {"frame_count": 0, "warnings": [DiagnosticWarning.BLANK_FRAME]}

    per_frame = [analyze_frame(f) for f in frames]
    brightnesses = [d["brightness"] for d in per_frame]
    all_warnings: set[str] = set()
    for d in per_frame:
        all_warnings.update(d["warnings"])

    # delta between consecutive frames
    deltas: list[float] = []
    for i in range(1, len(frames)):
        delta = float(np.abs(frames[i].astype(np.float32) - frames[i - 1].astype(np.float32)).mean())
        deltas.append(delta)

    avg_delta = float(np.mean(deltas)) if deltas else 0.0
    if avg_delta < 0.5:
        all_warnings.add(DiagnosticWarning.STATIC_RENDER)

    brightness_std = float(np.std(brightnesses))
    if brightness_std < 0.01:
        all_warnings.add(DiagnosticWarning.LOW_VARIETY)

    return {
        "frame_count": len(frames),
        "avg_brightness": float(np.mean(brightnesses)),
        "brightness_std": brightness_std,
        "avg_frame_delta": avg_delta,
        "warnings": sorted(all_warnings),
    }
