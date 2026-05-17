/**
 * Epic 02: Preview Console - Frontend types
 * Epic 12: Render Diagnostics - Frontend types
 *
 * Phase 05: Production Console UI components and state management
 */

// ============================================================================
// Epic 02: Preview Console Types
// ============================================================================

/**
 * Epic 02.B5, 02.B9: Render job status with phase awareness
 */
export enum RenderPhase {
  QUEUED = "queued",
  ANALYZING = "analyzing",
  RENDERING = "rendering",
  COMPLETED = "completed",
  FAILED = "failed",
}

export interface RenderJobStatus {
  job_id: string;
  phase: RenderPhase;
  status_text: string;

  // Analysis phase progress (0-100)
  analysis_current: number;
  analysis_total: number;
  analysis_percent: number;

  // Render phase progress (0-100)
  render_current: number;
  render_total: number;
  render_percent: number;

  // Overall progress
  overall_percent: number;

  // Error details (if failed)
  error_message?: string;

  // Timing
  started_at?: string;
  completed_at?: string;
}

/**
 * Epic 02.B6: Analysis phase progress tracking
 */
export interface AnalysisProgress {
  stage: string;
  current: number;
  total: number;
  percent: number;
  status_text: string;
}

/**
 * Epic 02.B7: Render progress tracking (every 200 frames)
 */
export interface RenderProgress {
  current_frame: number;
  total_frames: number;
  percent: number;
  frames_per_second: number;
  estimated_seconds_remaining: number;
}

/**
 * Epic 02.B4: Current canvas metadata
 */
export interface CanvasMetadata {
  schema_version: string;
  render_id: string;
  render_timestamp: string;
  frame_count: number;
  fps: number;
  duration: number;
  preset_id?: string;
  seed: number;
  compatibility_state: string;
}

/**
 * Epic 02.B8: Canvas naming request
 */
export interface CanvasNamingRequest {
  song_id: string;
  canvas_name: string;
  preset_ids?: string[];
  seed?: number;
  params?: Record<string, unknown>;
}

/**
 * Epic 02.F2: Server-owned song state
 */
export interface CurrentSongState {
  song_id: string;
  title?: string;
  duration?: number;
  current_canvas?: CurrentCanvasState;
}

export interface CurrentCanvasState {
  song_id: string;
  canvas_id?: string;
  render_artifact?: RenderArtifact;
  is_empty: boolean;
}

export interface RenderArtifact {
  metadata: CanvasMetadata;
  frames?: ChunkedBinaryFrames;
  timeline?: Record<string, unknown>;
  transitions?: Transition[];
}

export interface ChunkedBinaryFrames {
  chunk_size: number;
  total_chunks: number;
  chunk_paths: string[];
}

export interface Transition {
  type: string;
  alignment: string;
  duration: number;
  parameters?: Record<string, unknown>;
}

/**
 * Epic 02.F5, 02.F24, 02.F21: Main tab state
 */
export interface MainTabState {
  show_name: string;
  canvas_name: string;
  selected_presets: string[];
  is_rendering: boolean;
  render_error?: string;
}

/**
 * Epic 02.F6, 02.F13: Shader/Layer parameter tab
 */
export interface ShaderTabState {
  preset_id: string;
  preset_name: string;
  parameters: Record<string, unknown>;
  visible: boolean;
}

/**
 * Epic 02.F14: Timeline view state
 */
export interface TimelineViewState {
  scenes: SceneInfo[];
  transitions: TransitionInfo[];
  current_time: number;
  duration: number;
  is_playing: boolean;
}

export interface SceneInfo {
  scene_id: string;
  start_time: number;
  duration: number;
  preset_id: string;
  intensity: number;
  automation?: Record<string, unknown>;
}

export interface TransitionInfo {
  transition_id: string;
  type: string;
  start_time: number;
  duration: number;
  alignment: string;
}

/**
 * Epic 02.F15: Frame inspector state
 */
export interface FrameInspectorState {
  is_active: boolean;
  x_coord?: number;
  y_coord?: number;
  rgb_value?: [number, number, number];
}

/**
 * Epic 02.F17: A/B compare state
 */
export interface ABCompareState {
  render_a_id?: string;
  render_b_id?: string;
  is_comparing: boolean;
  split_position: number; // 0-100, position of vertical divider
}

/**
 * Epic 02.F18: Approval workflow state
 */
export interface ApprovalState {
  render_id?: string;
  is_approved: boolean;
  approval_notes?: string;
  approval_timestamp?: string;
}

/**
 * Epic 02.F11: Metadata panel display
 */
export interface MetadataDisplay {
  render_id: string;
  schema_version: string;
  preset_id?: string;
  seed: number;
  compatibility_state: string;
  frame_count: number;
  fps: number;
  duration: number;
  created_at: string;
}

// ============================================================================
// Epic 12: Render Diagnostics Types
// ============================================================================

/**
 * Epic 12.B1: Diagnostics summary metrics
 */
export interface DiagnosticsSummary {
  brightness_avg: number;
  brightness_min: number;
  brightness_max: number;
  color_avg: [number, number, number];
  frame_delta_avg: number;
  blank_frame_count: number;
  static_frame_count: number;
  render_duration_ms: number;
  total_frames: number;
}

/**
 * Epic 12.B2: Variety metrics for beat-response and section variation
 */
export interface VarietyMetrics {
  beat_response_score: number; // 0.0-1.0
  section_variation_score: number; // 0.0-1.0
  is_static: boolean;
  is_repetitive: boolean;
  warnings: string[];
}

/**
 * Epic 12.F2: Diagnostics display in console UI
 */
export interface DiagnosticsPanel {
  render_id: string;
  summary: DiagnosticsSummary;
  variety: VarietyMetrics;
  is_healthy: boolean;
}

/**
 * Epic 12.F3: Diagnostics assets (contact sheets, preview strips)
 */
export interface DiagnosticsAssets {
  render_id: string;
  contact_sheet_url?: string;
  preview_strip_url?: string;
  preview_gif_url?: string;
}

// ============================================================================
// Console State & UI Management
// ============================================================================

/**
 * Complete console state for Phase 05
 */
export interface ConsoleState {
  // Song & Canvas
  current_song?: CurrentSongState;
  current_canvas?: CurrentCanvasState;

  // Render Job
  active_render_job?: RenderJobStatus;
  render_history: RenderJobStatus[];

  // UI Tabs & Panels
  active_tab: string; // "main" or preset_id
  main_tab: MainTabState;
  shader_tabs: Map<string, ShaderTabState>;

  // Panel States
  timeline_view?: TimelineViewState;
  frame_inspector?: FrameInspectorState;
  ab_compare?: ABCompareState;
  approval?: ApprovalState;
  diagnostics?: DiagnosticsPanel;
  metadata?: MetadataDisplay;

  // UI Flags
  is_fullscreen: boolean;
  show_frame_inspector: boolean;
  show_diagnostics: boolean;
}

/**
 * Phase 05 UI events
 */
export interface ConsoleUIEvent {
  type:
    | "song_loaded"
    | "render_started"
    | "render_progress"
    | "render_completed"
    | "render_failed"
    | "canvas_approved"
    | "canvas_rejected"
    | "tab_changed"
    | "fullscreen_toggled"
    | "compare_activated";
  payload?: Record<string, unknown>;
}
