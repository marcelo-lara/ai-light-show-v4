import asyncio
import json
import os

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from render.artifact import ArtifactMetaV1, StatusBlock, make_render_id
from render.seed import validate_seed
from session.state import get_state
from ws.fanout import fanout

router = APIRouter(prefix="/api")

_job: dict = {
    "render_id": None,
    "phase": "idle",
    "current_frame": 0,
    "total_frames": 0,
    "error": None,
}


class RenderRequest(BaseModel):
    canvas_name: str
    preset_id: str = "bouncing_ball"
    seed: int
    params: dict = {}


@router.post("/render")
async def start_render(req: RenderRequest, bg: BackgroundTasks) -> dict:
    state = get_state()
    if state.current_song is None:
        raise HTTPException(status_code=400, detail="No song loaded")
    validate_seed(req.seed)
    render_id = make_render_id(
        state.current_song.song_id, req.preset_id, req.seed, req.params
    )
    _job.update(render_id=render_id, phase="queued", current_frame=0, total_frames=0, error=None)
    bg.add_task(_run_render, req, render_id, state.current_song.song_id)
    return {"render_id": render_id}


@router.get("/render/status")
def render_status() -> dict:
    return _job


async def _run_render(req: RenderRequest, render_id: str, song_id: str) -> None:
    try:
        _job["phase"] = "analysis"
        await fanout.broadcast({"type": "render_status", "data": dict(_job)})
        await asyncio.sleep(0.1)
        total = 300
        _job.update(phase="rendering", total_frames=total)
        for i in range(0, total, 30):
            _job["current_frame"] = i
            await fanout.broadcast({"type": "render_status", "data": dict(_job)})
            await asyncio.sleep(0)
        meta = ArtifactMetaV1(
            render_id=render_id,
            preset_id=req.preset_id,
            preset_version="1.0.0",
            seed=req.seed,
            params=req.params,
            song_id=song_id,
            analysis_id=f"{song_id}.analysis",
            fps=30.0,
            duration=10.0,
            frame_count=total,
            status=StatusBlock(state="done"),
        )
        _save_meta(song_id, req.canvas_name, meta)
        state = get_state()
        if req.canvas_name not in state.available_canvases:
            state.available_canvases.append(req.canvas_name)
        state.current_canvas = req.canvas_name
        _job.update(phase="done", current_frame=total)
        await fanout.broadcast({"type": "session_update", "data": state.model_dump()})
        await fanout.broadcast({"type": "render_status", "data": dict(_job)})
    except Exception as exc:
        _job.update(phase="failed", error=str(exc))
        await fanout.broadcast({"type": "render_status", "data": dict(_job)})


def _save_meta(song_id: str, canvas_name: str, meta: ArtifactMetaV1) -> None:
    d = os.path.join(os.getenv("DATA_DIR", "/data"), "artifacts")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{song_id}.{canvas_name}.meta.json")
    with open(path, "w") as f:
        json.dump(meta.model_dump(), f, indent=2)
