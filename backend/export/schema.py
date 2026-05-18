from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class FixtureLocation(BaseModel):
    x: float
    y: float
    z: float = 0.0


class FixtureInstance(BaseModel):
    id: str
    name: str
    fixture: str
    base_channel: int
    location: FixtureLocation


class PoiCalibration(BaseModel):
    pan: int = 0
    tilt: int = 0


class PointOfInterest(BaseModel):
    id: str
    name: str
    location: FixtureLocation
    fixtures: dict[str, PoiCalibration] = {}


class MappingConfig(BaseModel):
    pixel_order: Literal["linear", "serpentine"] = "linear"
    gamma: float = 1.0
    brightness_limit: float = 1.0
    canvas_width: int = 100
    canvas_height: int = 50
