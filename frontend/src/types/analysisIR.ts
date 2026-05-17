/**
 * Epic 03: Analysis IR (Intermediate Representation) types.
 *
 * These types mirror the Python AnalysisIR pydantic models in
 * backend/app/analysis_ir.py and are consumed by the frontend
 * analysis debug panel (03.F1, 03.F2).
 */

// ---------------------------------------------------------------------------
// Epic 03.F1: Schema constant
// ---------------------------------------------------------------------------

/** Must match ANALYSIS_SCHEMA_VERSION in backend/app/analysis_ir.py */
export const ANALYSIS_SCHEMA_VERSION = "1.0";

// ---------------------------------------------------------------------------
// Epic 03.F1: Sub-models
// ---------------------------------------------------------------------------

/** Smoothed per-band energy envelope (Epic 03.B4). */
export interface BandEnvelope {
  /** FFT band index (0 = sub-bass). */
  band_index: number;
  /** Normalised (0–1) energy values, one per analysis frame. */
  values: number[];
  /** Analysis sampling rate (frames per second). */
  sample_rate_fps: number;
}

/** Musical structure / section candidate with confidence score (Epic 03.B6). */
export interface SectionCandidate {
  start_time: number;
  end_time: number;
  /** One of: "downbeat" | "phrase" | "section" */
  type: string;
  /** Confidence 0–1. */
  confidence: number;
  /** Human-readable label, if known. */
  label?: string;
}

/** Analyzer provenance and debug stats (Epic 03.B7). */
export interface AnalysisDiagnostics {
  analyzer_version: string;
  analysis_schema_version: string;
  /** Overall beat-tracking confidence 0–1. */
  beat_confidence: number;
  source_metadata: Record<string, unknown>;
  debug_stats: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Epic 03.F1: Core AnalysisIR
// ---------------------------------------------------------------------------

/**
 * Versioned audio analysis IR consumed by the render system (Epic 03.B1).
 *
 * All per-frame arrays are aligned by index: entry `i` corresponds to time
 * `i / fps` seconds.
 */
export interface AnalysisIR {
  /** Schema version — matches ANALYSIS_SCHEMA_VERSION when valid. */
  schema_version: string;

  analysis_id: string;
  song_id: string;
  /** Song duration in seconds. */
  duration: number;
  /** Analysis sampling rate (frames per second). */
  fps: number;

  // Epic 03.B2: Beat timing
  beat_times: number[];
  beat_phase: number[];
  nearest_beat_distance: number[];

  // Epic 03.B3: Bar timing
  bar_times: number[];
  bar_phase: number[];

  // Epic 03.B4: Envelopes
  band_envelopes: BandEnvelope[];

  // Epic 03.B5: Global energy
  global_energy: number[];

  // Epic 03.B6: Structure
  structure_candidates: SectionCandidate[];

  // Epic 03.B7: Diagnostics
  diagnostics?: AnalysisDiagnostics;
}

// ---------------------------------------------------------------------------
// Epic 03.F2: Analysis debug / timestamp query types
// ---------------------------------------------------------------------------

/**
 * All render-time signals available at a specific timestamp (Epic 03.F2).
 *
 * Mirrors the dict returned by AnalysisTimestampQuery.at_time() on the backend.
 */
export interface AnalysisTimestampQueryResult {
  /** Queried time in seconds. */
  frame_time: number;
  /** Beat phase 0–1. */
  beat_phase: number;
  /** Bar phase 0–1. */
  bar_phase: number;
  /** Distance to nearest beat in seconds (non-negative). */
  nearest_beat_distance: number;
  /** Normalised global energy 0–1. */
  global_energy: number;
  /** Per-band energy values, one per BandEnvelope. */
  fft_bands: number[];
}

/** UI state for the analysis debug panel (Epic 03.F2). */
export interface AnalysisDebugState {
  analysis?: AnalysisIR;
  query_result?: AnalysisTimestampQueryResult;
  is_loading: boolean;
  error?: string;
}
