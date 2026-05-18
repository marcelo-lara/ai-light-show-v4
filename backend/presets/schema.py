from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from modulation.engine import ModulatorBinding


class ParamDef(BaseModel):
    id: str
    type: Literal["float", "int", "bool", "color", "enum"]
    default: Any
    min: float | None = None
    max: float | None = None
    step: float | None = None
    group: str | None = None


class RegisterDef(BaseModel):
    id: str
    default: float = 0.0
    min: float = -1e9
    max: float = 1e9


class MathBlock(BaseModel):
    preset_init: list[Any] = []
    frame: list[Any] = []


class LayerDef(BaseModel):
    id: str
    shader: str
    enabled: bool = True
    params: dict[str, Any] = {}
    modulators: dict[str, ModulatorBinding] = {}
    math: MathBlock = MathBlock()


class DisplayMeta(BaseModel):
    name: str
    tags: list[str] = []


class PresetV1(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    preset_id: str
    preset_version: int = 1
    display: DisplayMeta
    description: str = ""
    seed_policy: Literal["required", "derived"] = "required"
    params: list[ParamDef] = []
    registers: list[RegisterDef] = []
    math: MathBlock = MathBlock()
    layers: list[LayerDef] = []
