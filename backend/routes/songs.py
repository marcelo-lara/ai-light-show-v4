import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from session.state import CurrentSong, get_state
from ws.fanout import fanout

router = APIRouter(prefix="/api")

_AUDIO_EXTS = (".mp3", ".wav", ".flac")


class SongEntry(BaseModel):
    song_id: str
    name: str


class LoadSongRequest(BaseModel):
    song_id: str


def _songs_dir() -> str:
    return os.path.join(os.getenv("DATA_DIR", "/data"), "songs")


def _artifacts_dir() -> str:
    return os.path.join(os.getenv("DATA_DIR", "/data"), "artifacts")


@router.get("/songs")
def list_songs() -> list[SongEntry]:
    d = _songs_dir()
    if not os.path.isdir(d):
        return []
    return [
        SongEntry(song_id=os.path.splitext(f)[0], name=os.path.splitext(f)[0])
        for f in sorted(os.listdir(d))
        if f.lower().endswith(_AUDIO_EXTS)
    ]


@router.post("/songs/load")
async def load_song(req: LoadSongRequest) -> dict:
    d = _songs_dir()
    found = any(
        os.path.isfile(os.path.join(d, f"{req.song_id}{ext}")) for ext in _AUDIO_EXTS
    )
    if not found:
        raise HTTPException(status_code=404, detail=f"Song not found: {req.song_id}")
    state = get_state()
    state.current_song = CurrentSong(song_id=req.song_id, name=req.song_id)
    state.current_canvas = None
    state.available_canvases = _list_canvases(req.song_id)
    await fanout.broadcast({"type": "session_update", "data": state.model_dump()})
    return state.model_dump()


def _list_canvases(song_id: str) -> list[str]:
    d = _artifacts_dir()
    if not os.path.isdir(d):
        return []
    prefix, suffix = f"{song_id}.", ".meta.json"
    return [
        f[len(prefix) : -len(suffix)]
        for f in os.listdir(d)
        if f.startswith(prefix) and f.endswith(suffix)
    ]
