/**
 * Epic 06.F1-F3: Frontend types for Preset Schema
 * Epic 04.F1-F2: Frontend types for Layer Library
 * Epic 05.F1-F2: Frontend types for Modulation System
 * Epic 07.F1-F3: Frontend types for Raindrops Shader
 * Epic 08.F1-F3: Frontend types for Spectroid Chase Shader
 */

// ============================================================================
// Epic 06: Preset Schema Types
// ============================================================================

export enum ParameterType {
  FLOAT = "float",
  INT = "int",
  BOOLEAN = "boolean",
  STRING = "string",
  COLOR = "color",
  CHOICE = "choice",
}

export enum BlendMode {
  MAX = "max",
  ADD = "add",
  ALPHA = "alpha",
  MULTIPLY = "multiply",
  SCREEN = "screen",
  DIFFERENCE = "difference",
  MASK = "mask",
  REPLACE = "replace",
}

/**
 * Epic 06.F2: Parameter schema type for typed preset parameters and UI groups.
 */
export interface ParameterConstraint {
  min_value?: number;
  max_value?: number;
  step_size?: number;
  choices?: string[];
}

export interface ParameterSchema {
  name: string;
  type: ParameterType;
  label: string;
  description?: string;
  default_value: unknown;
  constraint?: ParameterConstraint;
  ui_group?: string;
}

/**
 * Epic 06.F1: Preset summary type with identity and labels.
 */
export interface PresetMetadata {
  preset_id: string;
  version: string;
  label: string;
  tags: string[];
  description?: string;
  author?: string;
  created_at?: string;
  modified_at?: string;
}

export interface ColorPalette {
  name: string;
  colors: Record<string, string>;
  description?: string;
}

export interface LayerReference {
  layer_id: string;
  label: string;
  order: number;
  blend_mode: BlendMode;
  enabled?: boolean;
  opacity?: number;
  params?: Record<string, unknown>;
}

/**
 * Epic 06.F1: Complete preset definition type for consuming schema-defined presets.
 */
export interface PresetDefinition {
  metadata: PresetMetadata;
  parameters: Record<string, ParameterSchema>;
  palette?: ColorPalette;
  layers: LayerReference[];
  default_blend_mode?: BlendMode;
}

/**
 * Epic 06.F3: Preset loading readiness - UI can consume presets without hardcoded assumptions.
 */
export interface PresetLoadingState {
  selected_preset?: PresetDefinition;
  presets: PresetDefinition[];
  is_loading: boolean;
  error?: string;
}

// ============================================================================
// Epic 04: Layer Library Types
// ============================================================================

/**
 * Epic 04.F1: Layer metadata type - layers are registry-backed with parameters.
 */
export interface LayerMetadata {
  layer_id: string;
  label: string;
  description?: string;
  parameter_schema: Record<string, ParameterSchema>;
  tags?: string[];
}

/**
 * Epic 04.F1: Complete layer info for parameter introspection.
 */
export interface LayerInfo extends LayerMetadata {
  blend_modes_supported: BlendMode[];
}

/**
 * Epic 04.F2: Layer browsing readiness - simple UI-facing shape for inspecting layers.
 */
export interface LayerBrowserState {
  layers: LayerInfo[];
  is_loading: boolean;
  selected_layer_id?: string;
  error?: string;
}

// ============================================================================
// Epic 05: Modulation System Types
// ============================================================================

export enum ModulatorType {
  AUDIO_BAND = "audio_band",
  AUDIO_ONSET = "audio_onset",
  BEAT_PULSE = "beat_pulse",
  BEAT_PHASE = "beat_phase",
  BAR_PHASE = "bar_phase",
  PHRASE_PROGRESS = "phrase_progress",
  LFO = "lfo",
  RANDOM = "random",
}

export enum LFOWaveform {
  SINE = "sine",
  TRIANGLE = "triangle",
  SQUARE = "square",
  SAWTOOTH = "sawtooth",
}

/**
 * Epic 05.F1: Modulator value types - current modulator values and mappings.
 */
export interface ModulatorValue {
  modulator_id: string;
  current_value: number;
  type: ModulatorType;
  label?: string;
}

export interface ModulatorBinding {
  parameter_name: string;
  modulator_id: string;
  mapping_operations?: string[];  // e.g., ["scale", "clamp", "smooth"]
}

/**
 * Epic 05.F2: Modulator inspection readiness - UI shape for viewing live modulator values.
 */
export interface ModulatorInspectionState {
  frame_time: number;
  beat_progress: number;
  bar_progress: number;
  phrase_progress: number;
  onset_detected: boolean;
  fft_bands: number[];
  active_bindings: ModulatorBinding[];
  modulator_values: Record<string, number>;
}

// ============================================================================
// Epic 07: Raindrops Shader Types
// ============================================================================

/**
 * Epic 07.F1: Shader metadata types for raindrops shader.
 */
export interface POI {
  id: string;
  x: number;
  y: number;
  name: string;
  type?: string;
}

export interface RaindropsShaderConfig {
  pulse_rate: number;
  pulse_radius_growth: number;
  pulse_decay: number;
  collision_strength: number;
  base_color: string;
  poi_ids?: string[];
}

/**
 * Epic 07.F2: POI selection readiness - UI can consume POI-backed shader controls.
 */
export interface POISelectionState {
  available_pois: POI[];
  selected_poi_ids: string[];
  is_loading: boolean;
}

// ============================================================================
// Epic 08: Spectroid Chase Shader Types
// ============================================================================

/**
 * Epic 08.F1: Shader metadata types for spectroid chase shader.
 */
export interface Fixture {
  id: string;
  x: number;
  y: number;
  type: string;
  name: string;
}

export interface SpectroidChaseConfig {
  trigger_sensitivity: number;
  line_length: number;
  chase_speed: number;
  fade_distance: number;
  line_width: number;
  base_color: string;
  parcan_ids?: string[];
}

/**
 * Epic 08.F2: Fixture-anchor readiness - UI can consume parcan and moving-head controls.
 */
export interface FixtureAnchorSelectionState {
  parcan_fixtures: Fixture[];
  moving_head_fixtures: Fixture[];
  selected_parcan_ids: string[];
  is_loading: boolean;
}

// ============================================================================
// Phase 03 UI State - Aggregated
// ============================================================================

export interface Phase03UIState {
  // Preset and layer systems
  presets: PresetLoadingState;
  layer_browser: LayerBrowserState;
  
  // Modulation inspection
  modulation_inspection: ModulatorInspectionState;
  
  // Shader-specific states
  raindrops_config?: RaindropsShaderConfig;
  raindrops_poi_selection: POISelectionState;
  
  spectroid_config?: SpectroidChaseConfig;
  spectroid_fixture_selection: FixtureAnchorSelectionState;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface PresetsListResponse {
  presets: PresetDefinition[];
  count: number;
}

export interface LayersListResponse {
  layers: LayerInfo[];
  count: number;
}

export interface LayerParametersResponse {
  layer_id: string;
  parameters: Record<string, ParameterSchema>;
}

export interface ModulatorInspectionResponse {
  frame_time: number;
  beat_progress: number;
  bar_progress: number;
  phrase_progress: number;
  onset_detected: boolean;
  fft_bands: number[];
  modulator_values: Record<string, number>;
}
