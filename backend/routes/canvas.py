import json
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from session.state import get_state
from ws.fanout import fanout

router = APIRouter(prefix="/api")


class SelectCanvasRequest(BaseModel):
    canvas_name: str


class ApproveRequest(BaseModel):
    approved: bool


@router.post("/canvas/select")
async def select_canvas(req: SelectCanvasRequest) -> dict:
    state = get_state()
    if req.canvas_name not in state.available_canvases:
        raise HTTPException(status_code=400, detail="Canvas not in available list")
    state.current_canvas = req.canvas_name
    await fanout.broadcast({"type": "session_update", "data": state.model_dump()})
    return {"current_canvas": req.canvas_name}


@router.put("/canvas/approve")
async def approve_canvas(req: ApproveRequest) -> dict:
    state = get_state()
    if state.current_canvas is None or state.current_song is None:
        raise HTTPException(status_code=400, detail="No canvas selected")
    path = _meta_path(state.current_song.song_id, state.current_canvas)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Artifact metadata not found")
    with open(path) as f:
        meta = json.load(f)
    meta.setdefault("status", {})["approved"] = req.approved
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)
    return {"approved": req.approved}


def _meta_path(song_id: str, canvas_name: str) -> str:
    d = os.path.join(os.getenv("DATA_DIR", "/data"), "artifacts")
    return os.path.join(d, f"{song_id}.{canvas_name}.meta.json")
