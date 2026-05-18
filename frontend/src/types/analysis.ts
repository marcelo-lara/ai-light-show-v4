export type BeatEvent = {
  time: number;
  confidence: number;
};

export type BarEvent = {
  time: number;
};

export type SectionCandidate = {
  start: number;
  end: number;
  label: string;
  confidence: number;
};

export type BandEnvelope = {
  band: "bass" | "mid" | "high";
  times: number[];
  values: number[];
};

export type AnalysisDiagnostics = {
  analyzer_version: string;
  analysis_duration_s: number;
  confidence: number;
  source_metadata: Record<string, unknown>;
};

export type AnalysisIRV1 = {
  schema_version: 1;
  analysis_id: string;
  song_id: string;
  duration: number;
  sample_rate: number;
  beats: BeatEvent[];
  bars: BarEvent[];
  downbeats: number[];
  sections: SectionCandidate[];
  band_envelopes: BandEnvelope[];
  energy_times: number[];
  energy_values: number[];
  diagnostics: AnalysisDiagnostics;
};

export type AnalysisSignals = {
  beat_phase: number;
  bar_phase: number;
  nearest_beat_distance: number;
  bass: number;
  mid: number;
  high: number;
  energy: number;
};
