from __future__ import annotations

import json
import os

from .schema import PresetV1
from .validator import validate_preset

_PRESETS_DIR = os.path.dirname(__file__)


def load_preset(preset_id: str) -> PresetV1:
    path = os.path.join(_PRESETS_DIR, f"{preset_id}.json")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Preset not found: {preset_id!r} (looked at {path})")
    with open(path) as f:
        raw = json.load(f)
    return validate_preset(raw)


def list_preset_ids() -> list[str]:
    return [
        os.path.splitext(f)[0]
        for f in sorted(os.listdir(_PRESETS_DIR))
        if f.endswith(".json")
    ]
