from __future__ import annotations

import math

import numpy as np

from shaders.types import FrameResult, LayerBase, LayerContext, LayerMeta
from shaders.registry import register


@register
class OceanWavesLayer(LayerBase):
    meta = LayerMeta(
        layer_id="ocean_waves",
        label="Ocean Waves",
        param_schema=[
            {"name": "base_color", "type": "color", "default": "#001a3a"},
            {"name": "highlight_color", "type": "color", "default": "#0077cc"},
            {"name": "wave_speed", "type": "float", "default": 0.35},
            {"name": "wave_scale", "type": "float", "default": 1.0},
        ],
    )

    def render(self, ctx: LayerContext) -> FrameResult:
        p = ctx.params
        speed = float(p.get("wave_speed", 0.35))
        scale = float(p.get("wave_scale", 1.0))
        base = _parse_color(str(p.get("base_color", "#001a3a")))
        high = _parse_color(str(p.get("highlight_color", "#0077cc")))

        t = ctx.time()
        drift = t * speed

        xs = np.linspace(0.0, 1.0, ctx.canvas_width)
        ys = np.linspace(0.0, 1.0, ctx.canvas_height)
        xg, yg = np.meshgrid(xs, ys)

        # three layered wave fields (per spec)
        swell = 0.5 + 0.5 * np.sin(2 * math.pi * (xg * 2.5 * scale - drift * 1.0))
        depth = 0.5 + 0.5 * np.cos(2 * math.pi * (xg * 1.3 * scale - drift * 0.7 + yg * 0.4))
        crest = np.clip((swell - 0.72) / 0.18, 0.0, 1.0) ** 2

        # smooth combined luminance
        lum = np.clip(swell * 0.55 + depth * 0.30 + crest * 0.15, 0.0, 1.0)
        lum = lum[:, :, np.newaxis]  # (H, W, 1)

        canvas = np.empty((ctx.canvas_height, ctx.canvas_width, 4), dtype=np.uint8)
        base_arr = np.array(base, dtype=np.float32) / 255.0
        high_arr = np.array(high, dtype=np.float32) / 255.0
        rgb = base_arr + lum * (high_arr - base_arr)
        canvas[:, :, :3] = np.clip(rgb * 255, 0, 255).astype(np.uint8)
        canvas[:, :, 3] = 255
        return canvas


def _parse_color(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 6:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return r, g, b
    return 0, 26, 58
