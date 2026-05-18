from __future__ import annotations

import numpy as np

from .registry import register
from .types import FrameResult, LayerBase, LayerContext, LayerMeta


def _hex_to_rgba(hex_color: str) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 6:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return r, g, b, 255
    if len(h) == 8:
        r, g, b, a = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16)
        return r, g, b, a
    return 255, 255, 255, 255


@register
class BouncingBallLayer(LayerBase):
    meta = LayerMeta(
        layer_id="bouncing_ball",
        label="Bouncing Ball",
        param_schema=[
            {"name": "start_x", "type": "int", "default": 10},
            {"name": "start_y", "type": "int", "default": 10},
            {"name": "velocity_x", "type": "int", "default": 1},
            {"name": "velocity_y", "type": "int", "default": 1},
            {"name": "color", "type": "color", "default": "#ffffff"},
        ],
    )

    def render(self, ctx: LayerContext) -> FrameResult:
        p = ctx.params
        x = int(p.get("start_x", 10))
        y = int(p.get("start_y", 10))
        vx = int(p.get("velocity_x", 1))
        vy = int(p.get("velocity_y", 1))
        color = str(p.get("color", "#ffffff"))
        r, g, b, a = _hex_to_rgba(color)
        W, H = ctx.canvas_width, ctx.canvas_height

        for _ in range(ctx.frame):
            nx, ny = x + vx, y + vy
            if nx < 0 or nx >= W:
                vx = -vx
                nx = x + vx
            if ny < 0 or ny >= H:
                vy = -vy
                ny = y + vy
            x, y = nx, ny

        frame = ctx.blank()
        frame[y, x] = [r, g, b, a]
        return frame
