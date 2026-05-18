export type DiagnosticsWarning =
  | "blank_frame"
  | "static_render"
  | "low_variety";

export type FrameDiagnostics = {
  brightness: number;
  avg_color: [number, number, number];
  warnings: DiagnosticsWarning[];
};

export type SequenceDiagnostics = {
  frame_count: number;
  avg_brightness: number;
  brightness_std: number;
  avg_frame_delta: number;
  warnings: DiagnosticsWarning[];
};
