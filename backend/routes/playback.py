from fastapi import APIRouter

from session.state import get_state
from ws.fanout import fanout

router = APIRouter(prefix="/api")


@router.post("/playback/play")
async def play() -> dict:
    state = get_state()
    state.playback.transport = "playing"
    await fanout.broadcast({"type": "session_update", "data": state.model_dump()})
    return {"transport": "playing"}


@router.post("/playback/pause")
async def pause() -> dict:
    state = get_state()
    state.playback.transport = "paused"
    await fanout.broadcast({"type": "session_update", "data": state.model_dump()})
    return {"transport": "paused"}


@router.post("/playback/stop")
async def stop() -> dict:
    state = get_state()
    state.playback.transport = "stopped"
    state.playback.position = 0.0
    await fanout.broadcast({"type": "session_update", "data": state.model_dump()})
    return {"transport": "stopped"}
