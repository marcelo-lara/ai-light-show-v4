import { create } from 'zustand';
import type { PlaybackState, CurrentSongState, CompatibilityErrorState } from '../types/renderContract';
import backendAPI from '../api/backend';

interface RenderJobState {
  jobId: string | null;
  phase: 'queued' | 'analyzing' | 'rendering' | 'completed' | 'failed';
  percent: number;
  statusText: string;
  errorMessage: string | null;
}

interface PlaybackStore {
  playbackState: PlaybackState | null;
  compatibilityError: CompatibilityErrorState;
  isLoading: boolean;

  // Epic 02: Render job tracking
  renderJob: RenderJobState;
  fixtures: Array<Record<string, unknown>>;
  pois: Array<Record<string, unknown>>;
  canvasName: string;

  // Actions
  loadPlaybackState: () => Promise<void>;
  loadSong: (songId: string) => Promise<void>;
  play: () => Promise<void>;
  stop: () => Promise<void>;
  setCompatibilityError: (error: CompatibilityErrorState) => void;
  clearCompatibilityError: () => void;
  
  // Epic 02 actions
  loadFixtures: () => Promise<void>;
  loadPOIs: () => Promise<void>;
  setCanvasName: (name: string) => void;
  startRender: (canvasName: string) => Promise<void>;
  updateRenderProgress: (
    phase: string,
    percent: number,
    statusText: string
  ) => void;
  completeRender: () => Promise<void>;
  failRender: (error: string) => void;
  clearRenderJob: () => void;
}

export const usePlaybackStore = create<PlaybackStore>((set) => ({
  playbackState: null,
  compatibilityError: {
    has_error: false,
    error_message: '',
  },
  isLoading: false,
  renderJob: {
    jobId: null,
    phase: 'queued',
    percent: 0,
    statusText: '',
    errorMessage: null,
  },
  fixtures: [],
  pois: [],
  canvasName: 'default',

  loadPlaybackState: async () => {
    set({ isLoading: true });
    try {
      const state = await backendAPI.getPlaybackState();
      set({ playbackState: state, isLoading: false });
    } catch (error) {
      console.error('Failed to load playback state:', error);
      set({ isLoading: false });
    }
  },

  loadSong: async (songId: string) => {
    set({ isLoading: true });
    try {
      const response = await backendAPI.loadSong(songId);
      set({
        playbackState: response.state,
        isLoading: false,
      });
    } catch (error) {
      console.error('Failed to load song:', error);
      set({
        compatibilityError: {
          has_error: true,
          error_message: `Failed to load song: ${error instanceof Error ? error.message : 'Unknown error'}`,
        },
        isLoading: false,
      });
    }
  },

  play: async () => {
    try {
      await backendAPI.play();
      set((state) => {
        if (state.playbackState) {
          return {
            playbackState: {
              ...state.playbackState,
              is_playing: true,
            },
          };
        }
        return state;
      });
    } catch (error) {
      console.error('Failed to play:', error);
    }
  },

  stop: async () => {
    try {
      await backendAPI.stop();
      set((state) => {
        if (state.playbackState) {
          return {
            playbackState: {
              ...state.playbackState,
              is_playing: false,
            },
          };
        }
        return state;
      });
    } catch (error) {
      console.error('Failed to stop:', error);
    }
  },

  setCompatibilityError: (error: CompatibilityErrorState) => {
    set({ compatibilityError: error });
  },

  clearCompatibilityError: () => {
    set({
      compatibilityError: {
        has_error: false,
        error_message: '',
      },
    });
  },

  // Epic 02: Fixture and POI loading
  loadFixtures: async () => {
    try {
      const data = await backendAPI.getFixtures();
      set({ fixtures: data.fixtures });
    } catch (error) {
      console.error('Failed to load fixtures:', error);
    }
  },

  loadPOIs: async () => {
    try {
      const data = await backendAPI.getPOIs();
      set({ pois: data.pois });
    } catch (error) {
      console.error('Failed to load POIs:', error);
    }
  },

  setCanvasName: (name: string) => {
    set({ canvasName: name });
  },

  // Epic 02: Render job management
  startRender: async (canvasName: string) => {
    try {
      const jobData = await backendAPI.startRender(canvasName);
      set({
        renderJob: {
          jobId: jobData.job_id,
          phase: 'queued',
          percent: 0,
          statusText: 'Queued for rendering',
          errorMessage: null,
        },
      });
    } catch (error) {
      console.error('Failed to start render:', error);
      set({
        renderJob: {
          jobId: null,
          phase: 'failed',
          percent: 0,
          statusText: 'Failed to start',
          errorMessage: error instanceof Error ? error.message : 'Unknown error',
        },
      });
    }
  },

  updateRenderProgress: (phase: string, percent: number, statusText: string) => {
    set((state) => ({
      renderJob: {
        ...state.renderJob,
        phase: (phase as any) || state.renderJob.phase,
        percent,
        statusText,
      },
    }));
  },

  completeRender: async () => {
    set((state) => ({
      renderJob: {
        ...state.renderJob,
        phase: 'completed',
        percent: 100,
        statusText: 'Render complete',
      },
    }));
  },

  failRender: (error: string) => {
    set({
      renderJob: {
        jobId: null,
        phase: 'failed',
        percent: 0,
        statusText: 'Render failed',
        errorMessage: error,
      },
    });
  },

  clearRenderJob: () => {
    set({
      renderJob: {
        jobId: null,
        phase: 'queued',
        percent: 0,
        statusText: '',
        errorMessage: null,
      },
    });
  },
}));
