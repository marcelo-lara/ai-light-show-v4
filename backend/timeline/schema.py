from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class SceneAutomation(BaseModel):
    param: str
    values: list[float] = []
    times: list[float] = []


class Scene(BaseModel):
    scene_id: str
    start: float
    end: float
    preset_id: str
    params: dict[str, Any] = {}
    seed: int = 0
    intensity: float = 1.0
    automation: list[SceneAutomation] = []


class TransitionDef(BaseModel):
    type: Literal["hard_cut", "crossfade", "beat_flash_cut"] = "hard_cut"
    alignment: Literal["beat", "bar", "section", "none"] = "beat"
    duration: float = 0.0


class TimelineV1(BaseModel):
    song_id: str
    source: Literal["auto_sections", "auto_beats", "manual"] = "auto_sections"
    scenes: list[Scene] = []
    transitions: dict[str, TransitionDef] = {}
