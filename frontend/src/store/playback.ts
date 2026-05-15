import { create } from 'zustand';
import type { PlaybackState, CurrentSongState, CompatibilityErrorState } from '../types/renderContract';
import backendAPI from '../api/backend';

interface PlaybackStore {
  playbackState: PlaybackState | null;
  compatibilityError: CompatibilityErrorState;
  isLoading: boolean;

  // Actions
  loadPlaybackState: () => Promise<void>;
  loadSong: (songId: string) => Promise<void>;
  play: () => Promise<void>;
  stop: () => Promise<void>;
  setCompatibilityError: (error: CompatibilityErrorState) => void;
  clearCompatibilityError: () => void;
}

export const usePlaybackStore = create<PlaybackStore>((set) => ({
  playbackState: null,
  compatibilityError: {
    has_error: false,
    error_message: '',
  },
  isLoading: false,

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
}));
