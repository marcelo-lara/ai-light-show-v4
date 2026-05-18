from typing import Literal

from pydantic import BaseModel, Field


class CurrentSong(BaseModel):
    song_id: str
    name: str


class PlaybackState(BaseModel):
    transport: Literal["stopped", "paused", "playing"] = "stopped"
    position: float = 0.0


class SessionState(BaseModel):
    current_song: CurrentSong | None = None
    current_canvas: str | None = None
    available_canvases: list[str] = Field(default_factory=list)
    playback: PlaybackState = Field(default_factory=PlaybackState)


_state = SessionState()


def get_state() -> SessionState:
    return _state


def reset_state() -> None:
    global _state
    _state = SessionState()
