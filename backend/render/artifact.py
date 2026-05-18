import hashlib
import json
from typing import Any, Literal

from pydantic import BaseModel, Field


class StatusBlock(BaseModel):
    state: Literal["pending", "rendering", "done", "failed"] = "pending"
    approved: bool = False
    error: str | None = None


class ArtifactMetaV1(BaseModel):
    schema_version: Literal[1] = 1
    render_id: str
    preset_id: str
    preset_version: str
    seed: int
    params: dict[str, Any]
    song_id: str
    analysis_id: str
    fps: float
    duration: float
    frame_count: int
    status: StatusBlock = Field(default_factory=StatusBlock)


def make_render_id(
    song_id: str,
    preset_id: str,
    seed: int,
    params: dict[str, Any],
) -> str:
    payload = json.dumps(
        {"song_id": song_id, "preset_id": preset_id, "seed": seed, "params": params},
        sort_keys=True,
    ).encode()
    return hashlib.sha256(payload).hexdigest()[:16]
