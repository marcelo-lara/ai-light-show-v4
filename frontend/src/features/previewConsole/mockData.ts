import type { ABCompareState, DiagnosticsPanel as DiagnosticsPanelType, TimelineViewState } from '../../types/phase05';
import type { PreviewPresetOption } from './types';

export const AVAILABLE_PRESETS: PreviewPresetOption[] = [
  { id: 'undersea_pulse_01', name: 'Undersea Pulse' },
  { id: 'undersea_waves', name: 'Undersea Waves' },
];

export const DEFAULT_COMPARE_STATE: ABCompareState = {
  is_comparing: false,
  split_position: 50,
};

export const createMockTimeline = (halfDuration: number, fullDuration: number): TimelineViewState => ({
  scenes: [
    { scene_id: 'scene_1', start_time: 0, duration: halfDuration, preset_id: 'undersea_pulse_01', intensity: 0.8 },
    { scene_id: 'scene_2', start_time: halfDuration, duration: halfDuration, preset_id: 'undersea_waves', intensity: 0.6 },
  ],
  transitions: [
    { transition_id: 'trans_1', type: 'crossfade', start_time: halfDuration, duration: 0.5, alignment: 'bar' },
  ],
  current_time: 0,
  duration: fullDuration,
  is_playing: false,
});

export const MOCK_DIAGNOSTICS: DiagnosticsPanelType = {
  render_id: 'render_12345',
  summary: {
    brightness_avg: 0.5,
    brightness_min: 0.1,
    brightness_max: 0.9,
    color_avg: [128, 100, 80],
    frame_delta_avg: 0.15,
    blank_frame_count: 2,
    static_frame_count: 5,
    render_duration_ms: 500,
    total_frames: 300,
  },
  variety: {
    beat_response_score: 0.75,
    section_variation_score: 0.65,
    is_static: false,
    is_repetitive: false,
    warnings: [],
  },
  is_healthy: true,
};