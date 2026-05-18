from __future__ import annotations

import math

import numpy as np

from .registry import register
from .types import FrameResult, LayerBase, LayerContext, LayerMeta


@register
class WaveLayer(LayerBase):
    meta = LayerMeta(
        layer_id="wave",
        label="Wave",
        param_schema=[
            {"name": "frequency", "type": "float", "default": 1.0},
            {"name": "speed", "type": "float", "default": 1.0},
            {"name": "amplitude", "type": "float", "default": 0.5},
        ],
    )

    def render(self, ctx: LayerContext) -> FrameResult:
        freq = float(ctx.params.get("frequency", 1.0))
        speed = float(ctx.params.get("speed", 1.0))
        amp = float(ctx.params.get("amplitude", 0.5))
        t = ctx.time()
        H, W = ctx.canvas_height, ctx.canvas_width
        frame = ctx.blank()
        xs = np.linspace(0, 2 * math.pi * freq, W)
        wave_y = ((np.sin(xs + t * speed * 2 * math.pi) * amp + 0.5) * (H - 1)).astype(int)
        wave_y = np.clip(wave_y, 0, H - 1)
        for x, y in enumerate(wave_y):
            frame[y, x] = [255, 255, 255, 255]
        return frame



