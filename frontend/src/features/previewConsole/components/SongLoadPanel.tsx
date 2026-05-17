import React from 'react';
import type { SongOption } from '../../../api/backend';

interface SongLoadPanelProps {
  selectedSongId: string;
  songs: SongOption[];
  onSongChange: (songId: string) => void;
  onLoadSong: () => void;
}

export const SongLoadPanel: React.FC<SongLoadPanelProps> = ({
  selectedSongId,
  songs,
  onSongChange,
  onLoadSong,
}) => (
  <div
    style={{
      padding: '16px',
      borderBottom: '1px solid #ddd',
    }}
  >
    <div
      style={{
        fontSize: '12px',
        fontWeight: 'bold',
        marginBottom: '8px',
      }}
    >
      Song
    </div>
    <select
      value={selectedSongId}
      onChange={(event) => onSongChange(event.target.value)}
      style={{
        width: '100%',
        padding: '8px',
        border: '1px solid #999',
        borderRadius: '3px',
        fontSize: '12px',
        marginBottom: '8px',
        boxSizing: 'border-box',
      }}
    >
      {songs.length === 0 ? (
        <option value="">No songs available</option>
      ) : (
        songs.map((song) => (
          <option key={song.id} value={song.id}>
            {song.title}
          </option>
        ))
      )}
    </select>
    <button
      onClick={onLoadSong}
      disabled={!selectedSongId}
      style={{
        width: '100%',
        padding: '10px',
        fontSize: '12px',
        fontWeight: 'bold',
        backgroundColor: selectedSongId ? '#333' : '#ccc',
        color: '#fff',
        border: 'none',
        borderRadius: '3px',
        cursor: selectedSongId ? 'pointer' : 'not-allowed',
      }}
    >
      Load Song
    </button>
  </div>
);

export default SongLoadPanel;