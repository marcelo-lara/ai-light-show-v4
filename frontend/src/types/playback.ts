export type TransportState = "stopped" | "paused" | "playing";

export type PlaybackState = {
  transport: TransportState;
  position: number;
};

export const STOPPED_PLAYBACK: PlaybackState = {
  transport: "stopped",
  position: 0,
};
