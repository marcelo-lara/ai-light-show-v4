import json
import os

from .schema import AnalysisIRV1, make_analysis_id


def _path(song_id: str, artifacts_dir: str) -> str:
    return os.path.join(artifacts_dir, f"{song_id}.analysis.json")


def load_cached(song_id: str, artifacts_dir: str) -> AnalysisIRV1 | None:
    expected_id = make_analysis_id(song_id)
    path = _path(song_id, artifacts_dir)
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        raw = json.load(f)
    if raw.get("analysis_id") != expected_id:
        return None
    return AnalysisIRV1.model_validate(raw)


def save_cache(ir: AnalysisIRV1, artifacts_dir: str) -> None:
    os.makedirs(artifacts_dir, exist_ok=True)
    with open(_path(ir.song_id, artifacts_dir), "w") as f:
        json.dump(ir.model_dump(), f, indent=2)
