from __future__ import annotations

import numpy as np

from shaders.types import FrameResult


def hard_cut(a: FrameResult, b: FrameResult, progress: float) -> FrameResult:
    return b.copy() if progress >= 0.5 else a.copy()


def crossfade(a: FrameResult, b: FrameResult, progress: float) -> FrameResult:
    t = float(np.clip(progress, 0.0, 1.0))
    blended = (a.astype(np.float32) * (1.0 - t) + b.astype(np.float32) * t)
    return np.clip(blended, 0, 255).astype(np.uint8)


def beat_flash_cut(
    a: FrameResult, b: FrameResult, progress: float, flash_color: tuple[int, int, int] = (255, 255, 255)
) -> FrameResult:
    if progress < 0.1:
        # flash frame
        flash = np.zeros_like(a)
        flash[:, :, 0] = flash_color[0]
        flash[:, :, 1] = flash_color[1]
        flash[:, :, 2] = flash_color[2]
        flash[:, :, 3] = 255
        return flash
    return b.copy()


_TRANSITION_FNS = {
    "hard_cut": hard_cut,
    "crossfade": crossfade,
    "beat_flash_cut": beat_flash_cut,
}


def apply_transition(
    kind: str, a: FrameResult, b: FrameResult, progress: float
) -> FrameResult:
    fn = _TRANSITION_FNS.get(kind)
    if fn is None:
        raise ValueError(f"Unknown transition type: {kind!r}")
    return fn(a, b, progress)
