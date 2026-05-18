from __future__ import annotations

import json
import os

import numpy as np

from .schema import FixtureInstance, MappingConfig, PointOfInterest

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "fixtures")


def load_fixtures(fixtures_path: str | None = None) -> list[FixtureInstance]:
    path = fixtures_path or os.path.join(_DATA_DIR, "fixtures.json")
    with open(path) as f:
        raw = json.load(f)
    return [FixtureInstance.model_validate(item) for item in raw]


def load_pois(pois_path: str | None = None) -> list[PointOfInterest]:
    path = pois_path or os.path.join(_DATA_DIR, "pois.json")
    with open(path) as f:
        raw = json.load(f)
    return [PointOfInterest.model_validate(item) for item in raw]


def sample_fixture_colors(
    frame: np.ndarray,
    fixtures: list[FixtureInstance],
    config: MappingConfig,
) -> list[dict]:
    h, w = frame.shape[:2]
    result = []
    for fx in fixtures:
        px = int(fx.location.x * (w - 1))
        py = int(fx.location.y * (h - 1))
        px = max(0, min(w - 1, px))
        py = max(0, min(h - 1, py))
        pixel = frame[py, px, :3].astype(np.float32) / 255.0
        pixel = np.clip(pixel * config.brightness_limit, 0.0, 1.0)
        if config.gamma != 1.0:
            pixel = np.power(pixel, 1.0 / config.gamma)
        r, g, b = (int(v * 255) for v in pixel)
        result.append({"fixture_id": fx.id, "r": r, "g": g, "b": b, "px": px, "py": py})
    return result


def build_pixel_order(config: MappingConfig) -> list[tuple[int, int]]:
    coords: list[tuple[int, int]] = []
    for row in range(config.canvas_height):
        if config.pixel_order == "serpentine" and row % 2 == 1:
            row_cols = range(config.canvas_width - 1, -1, -1)
        else:
            row_cols = range(config.canvas_width)
        for col in row_cols:
            coords.append((col, row))
    return coords
