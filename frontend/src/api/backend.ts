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
}

export default new BackendAPI();
