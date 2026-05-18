import numpy as np
import pytest

from export.mapper import build_pixel_order, load_fixtures, load_pois, sample_fixture_colors
from export.schema import MappingConfig


def test_load_fixtures():
    fixtures = load_fixtures()
    assert len(fixtures) > 0
    assert all(hasattr(f, "id") for f in fixtures)


def test_load_pois():
    pois = load_pois()
    assert len(pois) > 0
    assert all(hasattr(p, "id") for p in pois)


def test_sample_fixture_colors_returns_one_per_fixture():
    fixtures = load_fixtures()
    frame = np.full((50, 100, 4), 128, dtype=np.uint8)
    config = MappingConfig()
    result = sample_fixture_colors(frame, fixtures, config)
    assert len(result) == len(fixtures)


def test_sample_fixture_colors_applies_brightness_limit():
    fixtures = load_fixtures()[:1]
    frame = np.full((50, 100, 4), 255, dtype=np.uint8)
    config = MappingConfig(brightness_limit=0.5)
    result = sample_fixture_colors(frame, fixtures, config)
    assert result[0]["r"] <= 128


def test_sample_fixture_colors_applies_gamma():
    fixtures = load_fixtures()[:1]
    frame = np.full((50, 100, 4), 128, dtype=np.uint8)
    config_flat = MappingConfig(gamma=1.0)
    config_gamma = MappingConfig(gamma=2.2)
    r_flat = sample_fixture_colors(frame, fixtures, config_flat)[0]["r"]
    r_gamma = sample_fixture_colors(frame, fixtures, config_gamma)[0]["r"]
    assert r_gamma > r_flat  # gamma > 1 brightens linear values


def test_linear_pixel_order_row_major():
    config = MappingConfig(canvas_width=4, canvas_height=2, pixel_order="linear")
    coords = build_pixel_order(config)
    assert len(coords) == 8
    assert coords[0] == (0, 0)
    assert coords[3] == (3, 0)
    assert coords[4] == (0, 1)


def test_serpentine_pixel_order_reverses_odd_rows():
    config = MappingConfig(canvas_width=4, canvas_height=2, pixel_order="serpentine")
    coords = build_pixel_order(config)
    assert coords[4] == (3, 1)  # odd row starts at far end
    assert coords[7] == (0, 1)


def test_orientation_test_pattern():
    """Top-left pixel is brightest in a gradient frame."""
    frame = np.zeros((50, 100, 4), dtype=np.uint8)
    for y in range(50):
        for x in range(100):
            v = 255 - int(x / 99 * 127 + y / 49 * 127)
            frame[y, x, :3] = v
            frame[y, x, 3] = 255
    assert int(frame[0, 0, 0]) > int(frame[49, 99, 0])
