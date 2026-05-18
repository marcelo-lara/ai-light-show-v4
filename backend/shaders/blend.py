from __future__ import annotations

import numpy as np

from .types import FrameResult

_MODES = {"max", "add", "alpha", "multiply", "screen", "difference", "mask"}


def blend(base: FrameResult, over: FrameResult, mode: str = "alpha") -> FrameResult:
    if mode not in _MODES:
        raise ValueError(f"Unknown blend mode: {mode!r}")
    b = base.astype(np.float32) / 255.0
    o = over.astype(np.float32) / 255.0
    if mode == "max":
        out = np.maximum(b, o)
    elif mode == "add":
        out = np.clip(b + o, 0, 1)
    elif mode == "alpha":
        a = o[..., 3:4]
        out = b * (1 - a) + o * a
    elif mode == "multiply":
        out = b * o
    elif mode == "screen":
        out = 1 - (1 - b) * (1 - o)
    elif mode == "difference":
        out = np.abs(b - o)
    elif mode == "mask":
        mask = o[..., 3:4]
        out = b * mask
    else:
        out = b
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
