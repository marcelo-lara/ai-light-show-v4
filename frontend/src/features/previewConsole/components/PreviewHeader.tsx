import React from 'react';

interface PreviewHeaderProps {
  canvasName: string;
  currentSongId?: string;
}

export const PreviewHeader: React.FC<PreviewHeaderProps> = ({
  canvasName,
  currentSongId,
}) => (
  <div
    style={{
      backgroundColor: '#333',
      color: '#fff',
      padding: '12px 16px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      borderBottom: '2px solid #2196f3',
    }}
  >
    <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
      {canvasName ? `Canvas: ${canvasName}` : 'AI Light Show - Production Console'}
    </div>
    <div style={{ fontSize: '11px', color: '#aaa' }}>
      {currentSongId ? `Song: ${currentSongId}` : 'No song loaded'} | v0.5.0
    </div>
  </div>
);

export default PreviewHeader;