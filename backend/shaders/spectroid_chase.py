from __future__ import annotations

import numpy as np

from shaders.types import FrameResult, LayerBase, LayerContext, LayerMeta
from shaders.registry import register

_DEFAULT_ANCHORS = [(0.2, 0.5), (0.5, 0.5), (0.8, 0.5)]


@register
class SpectroidChaseLayer(LayerBase):
    meta = LayerMeta(
        layer_id="spectroid_chase",
        label="Spectroid Chase",
        param_schema=[
            {"name": "color", "type": "color", "default": "#ff8800"},
            {"name": "line_length", "type": "float", "default": 0.4},
            {"name": "spread", "type": "float", "default": 0.08},
            {"name": "fade", "type": "float", "default": 0.85},
            {"name": "chase_speed", "type": "float", "default": 1.0},
            {"name": "sensitivity", "type": "float", "default": 0.5},
        ],
    )

    def render(self, ctx: LayerContext) -> FrameResult:
        p = ctx.params
        color_hex = str(p.get("color", "#ff8800"))
        line_length = float(p.get("line_length", 0.4))
        spread = float(p.get("spread", 0.08))
        fade = float(p.get("fade", 0.85))
        chase_speed = float(p.get("chase_speed", 1.0))
        sensitivity = float(p.get("sensitivity", 0.5))

        trigger = max(ctx.signals.energy - (1.0 - sensitivity), 0.0) / max(sensitivity, 0.01)
        intensity = min(trigger * ctx.signals.beat_pulse if hasattr(ctx.signals, "beat_pulse") else trigger, 1.0)

        t = ctx.time()
        W, H = ctx.canvas_width, ctx.canvas_height
        xs = np.arange(W, dtype=np.float32) / W
        ys = np.arange(H, dtype=np.float32) / H
        xg, yg = np.meshgrid(xs, ys)

        accumulated = np.zeros((H, W), dtype=np.float32)
        for ax, ay in _DEFAULT_ANCHORS:
            chase_x = ax + (xs - ax) * (t * chase_speed % 1.0)
            for cx in chase_x[::4]:
                dx = xg - cx
                dy = yg - ay
                line_mask = (np.abs(dx) < line_length) & (np.abs(dy) < spread)
                dist = np.abs(dx) / line_length
                accumulated += np.where(line_mask, (1.0 - dist) * fade, 0.0)

        lum = np.clip(accumulated * intensity, 0.0, 1.0)
        r, g, b = _parse_color(color_hex)
        canvas = ctx.blank()
        canvas[:, :, 0] = (lum * r).astype(np.uint8)
        canvas[:, :, 1] = (lum * g).astype(np.uint8)
        canvas[:, :, 2] = (lum * b).astype(np.uint8)
        canvas[:, :, 3] = np.clip(lum * 255, 0, 255).astype(np.uint8)
        return canvas


def _parse_color(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 6:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 255, 136, 0
