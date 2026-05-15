/**
 * Epic 01.F1: Frontend types matching backend render artifact contract
 */

export interface RenderArtifactMetadata {
  schema_version: string;
  render_id: string;
  preset_id: string;
  preset_version: string;
  seed: number;
  song_id: string;
  analysis_id: string;
  fps: number;
  duration: number;
  frame_count: number;
  params?: Record<string, unknown>;
  created_at?: string;
  created_by?: string;
}

export interface ChunkedBinaryFrames {
  chunk_size: number;
  total_chunks: number;
  chunk_paths: string[];
}

export interface RenderArtifact {
  metadata: RenderArtifactMetadata;
  frames?: ChunkedBinaryFrames;
  checksum?: string;
}

export interface CurrentCanvasState {
  song_id: string;
  canvas_id?: string;
  render_artifact?: RenderArtifact;
  is_empty: boolean;
}

export interface CurrentSongState {
  song_id: string;
  title?: string;
  duration?: number;
  analysis_id?: string;
  current_canvas?: CurrentCanvasState;
  created_at?: string;
}

export interface PlaybackState {
  current_song?: CurrentSongState;
  is_playing: boolean;
  playback_time: number;
}

/**
 * Epic 01.F2: Frontend compatibility state
 */
export interface ArtifactCompatibilityError {
  error: string;
  is_compatible: false;
  render_id?: string;
}

export interface ArtifactCompatibilitySuccess {
  is_compatible: true;
  schema_version: string;
  render_id: string;
}

export type ArtifactCompatibilityResult =
  | ArtifactCompatibilityError
  | ArtifactCompatibilitySuccess;

/**
 * UI State for displaying compatibility errors
 */
export interface CompatibilityErrorState {
  has_error: boolean;
  error_message: string;
  incompatible_render_id?: string;
  suggested_action?: string;
}
