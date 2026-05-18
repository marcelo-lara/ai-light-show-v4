export type SceneAutomation = {
  param: string;
  values: number[];
  times: number[];
};

export type Scene = {
  scene_id: string;
  start: number;
  end: number;
  preset_id: string;
  params: Record<string, unknown>;
  seed: number;
  intensity: number;
  automation: SceneAutomation[];
};

export type TransitionDef = {
  type: "hard_cut" | "crossfade" | "beat_flash_cut";
  alignment: "beat" | "bar" | "section" | "none";
  duration: number;
};

export type TimelineV1 = {
  song_id: string;
  source: "auto_sections" | "auto_beats" | "manual";
  scenes: Scene[];
  transitions: Record<string, TransitionDef>;
};
