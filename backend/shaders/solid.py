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
class SolidLayer(LayerBase):
    meta = LayerMeta(
        layer_id="solid",
        label="Solid Fill",
        param_schema=[{"name": "color", "type": "color", "default": "#ffffff"}],
    )

    def render(self, ctx: LayerContext) -> FrameResult:
        color = str(ctx.params.get("color", "#ffffff"))
        r, g, b, a = _hex_to_rgba(color)
        frame = ctx.blank()
        frame[:, :] = [r, g, b, a]
        return frame



