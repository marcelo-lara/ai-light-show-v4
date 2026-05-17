import { useEffect } from 'react';
import type { Dispatch, SetStateAction } from 'react';
import type { SongOption } from '../../../api/backend';

interface UsePreviewConsoleBootstrapOptions {
  loadPlaybackState: () => Promise<void>;
  loadSongs: () => Promise<void>;
  loadFixtures: () => Promise<void>;
  loadPOIs: () => Promise<void>;
  playbackSongId?: string;
  selectedSongId: string;
  setSelectedSongId: Dispatch<SetStateAction<string>>;
  songs: SongOption[];
}

export const usePreviewConsoleBootstrap = ({
  loadPlaybackState,
  loadSongs,
  loadFixtures,
  loadPOIs,
  playbackSongId,
  selectedSongId,
  setSelectedSongId,
  songs,
}: UsePreviewConsoleBootstrapOptions): void => {
  useEffect(() => {
    void loadPlaybackState();
    void loadSongs();
    void loadFixtures();
    void loadPOIs();
  }, [loadPlaybackState, loadSongs, loadFixtures, loadPOIs]);

  useEffect(() => {
    if (playbackSongId) {
      setSelectedSongId(playbackSongId);
      return;
    }

    if (!selectedSongId && songs.length > 0) {
      setSelectedSongId(songs[0].id);
    }
  }, [playbackSongId, selectedSongId, setSelectedSongId, songs]);
};