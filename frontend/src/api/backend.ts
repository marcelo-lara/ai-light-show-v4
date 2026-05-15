import axios, { AxiosInstance } from 'axios';
import type {
  PlaybackState,
  CurrentSongState,
  RenderArtifact,
  ArtifactCompatibilityResult,
} from '../types/renderContract';

class BackendAPI {
  private client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:3401') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Playback state management
  async getPlaybackState(): Promise<PlaybackState> {
    const response = await this.client.get<PlaybackState>('/api/playback/state');
    return response.data;
  }

  // Song loading (backend-owned)
  async loadSong(songId: string): Promise<{ status: string; state: PlaybackState }> {
    const response = await this.client.post(`/api/songs/${songId}/load`);
    return response.data;
  }

  // Render ID generation (Epic 01.B2)
  async generateRenderID(
    songId: string,
    presetId: string,
    seed: number,
    params?: Record<string, unknown>
  ): Promise<{ render_id: string }> {
    const response = await this.client.post('/api/render/generate-id', null, {
      params: {
        song_id: songId,
        preset_id: presetId,
        seed,
        params: params || {},
      },
    });
    return response.data;
  }

  // Artifact validation (Epic 01.B4)
  async validateArtifact(artifact: Record<string, unknown>): Promise<ArtifactCompatibilityResult> {
    const response = await this.client.post<ArtifactCompatibilityResult>(
      '/api/render/validate',
      artifact
    );
    return response.data;
  }

  // Get render status
  async getRenderStatus(renderId: string): Promise<{ status: string }> {
    const response = await this.client.get(`/api/render/${renderId}/status`);
    return response.data;
  }

  // Playback controls
  async play(): Promise<{ status: string }> {
    const response = await this.client.post('/api/playback/play');
    return response.data;
  }

  async stop(): Promise<{ status: string }> {
    const response = await this.client.post('/api/playback/stop');
    return response.data;
  }

  // Epic 02: Fixtures and POIs
  async getFixtures(): Promise<{
    fixtures: Array<Record<string, unknown>>;
    schema_version: string;
  }> {
    const response = await this.client.get('/api/fixtures');
    return response.data;
  }

  async getPOIs(): Promise<{
    pois: Array<Record<string, unknown>>;
    schema_version: string;
  }> {
    const response = await this.client.get('/api/pois');
    return response.data;
  }

  // Epic 02: Render job management
  async startRender(canvasName: string, presetIds?: string[], seed?: number) {
    const response = await this.client.post('/api/render/start', {
      canvas_name: canvasName,
      preset_ids: presetIds,
      seed,
    });
    return response.data;
  }

  async getRenderStatus(jobId: string): Promise<Record<string, unknown>> {
    const response = await this.client.get(`/api/render/${jobId}/status`);
    return response.data;
  }

  async completeRender(jobId: string): Promise<Record<string, unknown>> {
    const response = await this.client.post(`/api/render/${jobId}/complete`, {});
    return response.data;
  }

  async failRender(jobId: string, errorMessage: string): Promise<Record<string, unknown>> {
    const response = await this.client.post(`/api/render/${jobId}/fail`, {
      error_message: errorMessage,
    });
    return response.data;
  }
}

export default new BackendAPI();
