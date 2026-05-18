import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from session.state import get_state
from ws.fanout import fanout

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await fanout.connect(ws)
    state = get_state()
    await ws.send_text(json.dumps({"type": "session_update", "data": state.model_dump()}))
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        fanout.disconnect(ws)
