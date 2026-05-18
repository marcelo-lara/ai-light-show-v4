from __future__ import annotations

import numpy as np

from .registry import register
from .types import FrameResult, LayerBase, LayerContext, LayerMeta


def _hex_to_rgba(hex_color: str) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 6:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return r, g, b, 255
    return 255, 255, 255, 255


@register
class GradientLayer(LayerBase):
    meta = LayerMeta(
        layer_id="gradient",
        label="Gradient Fill",
        param_schema=[
            {"name": "color_a", "type": "color", "default": "#000000"},
            {"name": "color_b", "type": "color", "default": "#ffffff"},
            {"name": "axis", "type": "str", "default": "x"},
        ],
    )

    def render(self, ctx: LayerContext) -> FrameResult:
        ca = _hex_to_rgba(str(ctx.params.get("color_a", "#000000")))
        cb = _hex_to_rgba(str(ctx.params.get("color_b", "#ffffff")))
        axis = str(ctx.params.get("axis", "x"))
        H, W = ctx.canvas_height, ctx.canvas_width
        frame = ctx.blank()
        if axis == "x":
            t = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
        else:
            t = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        a_arr = np.array(ca, dtype=np.float32)
        b_arr = np.array(cb, dtype=np.float32)
        frame[:] = (a_arr * (1 - t) + b_arr * t).astype(np.uint8)
        return frame
