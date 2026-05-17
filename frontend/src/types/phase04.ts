/**
 * Epic 09.F1-F2: Frontend types for Timeline Director
 * Epic 10.F1-F2: Frontend types for Transition System
 */

// ============================================================================
// Epic 09: Timeline Director Types
// ============================================================================

export enum AlignmentType {
  BEAT = "beat",
  BAR = "bar",
  PHRASE = "phrase",
  SECTION = "section",
  FRAME = "frame",
}

export enum InterpolationType {
  LINEAR = "linear",
  EASE_IN = "ease_in",
  EASE_OUT = "ease_out",
  EASE_IN_OUT = "ease_in_out",
  STEP = "step",
}

/**
 * Epic 09.F1: Control point for automation curves.
 */
export interface ControlPoint {
  time: number; // seconds from scene start
  value: number; // normalized 0-1
}

/**
 * Epic 09.F1: Automation curve for intensity or parameters.
 */
export interface AutomationCurve {
  name: string;
  interpolation: InterpolationType;
  control_points: ControlPoint[];
}

/**
 * Epic 09.F1: Scene metadata and timing.
 */
export interface Scene {
  scene_id: string;
  start_time: number;
  end_time: number;

  // Musical alignment
  start_beat?: number;
  start_bar?: number;
  start_phrase?: number;
  start_section?: number;

  // Preset and rendering
  preset_id: string;
  seed: number;
  params: Record<string, unknown>;

  // Automation
  intensity: number;
  intensity_automation?: AutomationCurve;
  param_automation: Record<string, AutomationCurve>;

  // Metadata
  metadata?: Record<string, unknown>;
  is_auto_generated: boolean;
  is_manual_override: boolean;
}

/**
 * Epic 09.F1: Timeline collection.
 */
export interface SceneTimeline {
  timeline_id: string;
  song_id: string;
  duration: number;
  scenes: Scene[];
  auto_generated: boolean;
  generation_method?: "sections" | "phrases" | "beats";
  created_at: string;
}

/**
 * Epic 09.F2: Timeline UI state for future editor.
 */
export interface TimelineUIState {
  timeline: SceneTimeline;
  selected_scene_id?: string;
  is_editing: boolean;
  error?: string;
  playback_time?: number;
}

/**
 * Epic 09.F1: Timeline metadata for artifacts.
 */
export interface TimelineMetadata {
  has_timeline: boolean;
  timeline_id?: string;
  scene_count?: number;
  generation_method?: string;
}

// ============================================================================
// Epic 10: Transition System Types
// ============================================================================

export enum TransitionType {
  HARD_CUT = "hard_cut",
  CROSSFADE = "crossfade",
  BEAT_FLASH_CUT = "beat_flash_cut",
}

/**
 * Epic 10.F1: Transition model.
 */
export interface Transition {
  transition_id: string;
  from_scene_id: string;
  to_scene_id: string;

  // Type and timing
  type: TransitionType;
  alignment: AlignmentType;
  duration: number;

  // Timing info
  start_time: number;
  end_time?: number;

  // Musical alignment
  start_beat?: number;
  start_bar?: number;
  start_phrase?: number;
  start_section?: number;

  // Transition-specific parameters
  params: Record<string, unknown>;

  // Metadata
  metadata?: Record<string, unknown>;
  created_at: string;
}

/**
 * Epic 10.F2: Transition UI state for preview.
 */
export interface TransitionUIState {
  transition: Transition;
  preview_frame?: number;
  is_previewing: boolean;
  error?: string;
}

/**
 * Epic 10.F1: Transition metadata for artifacts.
 */
export interface TransitionMetadata {
  has_transitions: boolean;
  transition_count?: number;
  transition_types?: TransitionType[];
}

/**
 * Epic 10.B7: Debug information for transitions.
 */
export interface TransitionDebugInfo {
  transition_id: string;
  type: TransitionType;
  start_time: number;
  end_time: number;
  duration: number;
  progress_at_sample?: number;
  alignment_info: Record<string, unknown>;
  parameter_snapshot: Record<string, unknown>;
}

// ============================================================================
// Integrated Types
// ============================================================================

/**
 * Complete timeline information for render artifacts (Phase 04).
 */
export interface TimelineRenderInfo {
  timeline?: SceneTimeline;
  transitions?: Transition[];
  timeline_metadata: TimelineMetadata;
  transition_metadata: TransitionMetadata;
}
