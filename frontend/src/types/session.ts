import type { PlaybackState } from "./playback";

export type CurrentSong = {
  song_id: string;
  name: string;
};

export type SessionState = {
  current_song: CurrentSong | null;
  current_canvas: string | null;
  available_canvases: string[];
  playback: PlaybackState;
};

export const EMPTY_SESSION: SessionState = {
  current_song: null,
  current_canvas: null,
  available_canvases: [],
  playback: { transport: "stopped", position: 0 },
};
