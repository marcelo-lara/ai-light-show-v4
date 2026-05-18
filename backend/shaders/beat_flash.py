from __future__ import annotations

from .registry import register
from .types import FrameResult, LayerBase, LayerContext, LayerMeta


@register
class BeatFlashLayer(LayerBase):
    meta = LayerMeta(
        layer_id="beat_flash",
        label="Beat Flash",
        param_schema=[
            {"name": "color", "type": "color", "default": "#ffffff"},
            {"name": "decay", "type": "float", "default": 0.8},
        ],
    )

    def render(self, ctx: LayerContext) -> FrameResult:
        color = str(ctx.params.get("color", "#ffffff"))
        decay = float(ctx.params.get("decay", 0.8))
        hx = color.lstrip("#")
        r, g, b = int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)
        phase = ctx.signals.beat_phase
        brightness = max(0.0, (1.0 - phase) ** decay)
        frame = ctx.blank()
        frame[:, :] = [
            int(r * brightness),
            int(g * brightness),
            int(b * brightness),
            int(255 * brightness),
        ]
        return frame
