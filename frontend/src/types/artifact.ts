export type ArtifactStatusState = "pending" | "rendering" | "done" | "failed";

export type ArtifactStatus = {
  state: ArtifactStatusState;
  approved: boolean;
  error: string | null;
};

export type ArtifactMetaV1 = {
  schema_version: 1;
  render_id: string;
  preset_id: string;
  preset_version: string;
  seed: number;
  params: Record<string, unknown>;
  song_id: string;
  analysis_id: string;
  fps: number;
  duration: number;
  frame_count: number;
  status: ArtifactStatus;
};

export function isCompatibleArtifact(raw: unknown): raw is ArtifactMetaV1 {
  if (typeof raw !== "object" || raw === null) return false;
  return (raw as Record<string, unknown>)["schema_version"] === 1;
}
