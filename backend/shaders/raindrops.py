from __future__ import annotations

import math

import numpy as np

from shaders.types import FrameResult, LayerBase, LayerContext, LayerMeta
from shaders.registry import register


@register
class RaindropsLayer(LayerBase):
    meta = LayerMeta(
        layer_id="raindrops",
        label="Raindrops",
        param_schema=[
            {"name": "pulse_rate", "type": "float", "default": 1.0},
            {"name": "radius_growth", "type": "float", "default": 0.3},
            {"name": "decay", "type": "float", "default": 0.8},
            {"name": "color", "type": "color", "default": "#88ccff"},
            {"name": "poi_ids", "type": "str", "default": ""},
            {"name": "collision_strength", "type": "float", "default": 1.5},
        ],
    )

    def render(self, ctx: LayerContext) -> FrameResult:
        p = ctx.params
        color_hex = str(p.get("color", "#88ccff"))
        pulse_rate = float(p.get("pulse_rate", 1.0))
        radius_growth = float(p.get("radius_growth", 0.3))
        decay = float(p.get("decay", 0.8))
        collision_strength = float(p.get("collision_strength", 1.5))
        poi_raw = str(p.get("poi_ids", ""))

        origins = _get_poi_coords(poi_raw, ctx.canvas_width, ctx.canvas_height)
        if not origins:
            origins = [(ctx.canvas_width // 2, ctx.canvas_height // 2)]

        t = ctx.time()
        period = 1.0 / max(pulse_rate, 0.01)
        max_r = math.sqrt(ctx.canvas_width ** 2 + ctx.canvas_height ** 2)

        xs = np.arange(ctx.canvas_width, dtype=np.float32)
        ys = np.arange(ctx.canvas_height, dtype=np.float32)
        xg, yg = np.meshgrid(xs, ys)

        accumulated = np.zeros((ctx.canvas_height, ctx.canvas_width), dtype=np.float32)
        for ox, oy in origins:
            phase = (t % period) / period
            current_r = phase * max_r * radius_growth
            dist = np.sqrt((xg - ox) ** 2 + (yg - oy) ** 2)
            ring = np.exp(-((dist - current_r) ** 2) / (2.0 * 8.0 ** 2))
            accumulated += ring

        # collision: boost where multiple rings overlap
        collision_mask = accumulated > (len(origins) * 0.7)
        accumulated = np.where(collision_mask, accumulated * collision_strength, accumulated)
        lum = np.clip(accumulated * decay, 0.0, 1.0)

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
    return 136, 204, 255


def _get_poi_coords(
    poi_raw: str, width: int, height: int
) -> list[tuple[int, int]]:
    """Return pixel coords from comma-separated 'x:y' fraction pairs."""
    coords: list[tuple[int, int]] = []
    for tok in poi_raw.split(","):
        tok = tok.strip()
        if ":" in tok:
            try:
                fx, fy = tok.split(":")
                coords.append((int(float(fx) * width), int(float(fy) * height)))
            except (ValueError, TypeError):
                pass
    return coords
