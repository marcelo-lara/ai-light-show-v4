from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from analysis.schema import AnalysisSignals

# RGBA frame: shape (H, W, 4), dtype uint8
FrameResult = np.ndarray


@dataclass
class LayerContext:
    frame: int
    fps: float
    seed: int
    params: dict[str, Any]
    signals: AnalysisSignals
    canvas_width: int = 100
    canvas_height: int = 50

    def blank(self) -> FrameResult:
        return np.zeros((self.canvas_height, self.canvas_width, 4), dtype=np.uint8)

    def time(self) -> float:
        return self.frame / max(self.fps, 1e-6)


@dataclass
class LayerMeta:
    layer_id: str
    label: str
    param_schema: list[dict[str, Any]] = field(default_factory=list)


class LayerBase:
    meta: LayerMeta

    def render(self, ctx: LayerContext) -> FrameResult:
        raise NotImplementedError
