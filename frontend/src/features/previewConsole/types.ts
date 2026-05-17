export interface PreviewPresetOption {
  id: string;
  name: string;
}

export interface RenderStartParams {
  show_name: string;
  canvas_name: string;
  selected_presets: string[];
}

export interface OverlayFixture {
  fixture_id: string;
  canvas_anchor?: {
    x: number;
    y: number;
  };
}

export interface OverlayPOI {
  poi_id: string;
  canvas_pos: {
    x: number;
    y: number;
  };
}