import React from 'react';

interface MetadataDisplayProps {
  metadata: {
    schema_version?: string;
    render_id?: string;
    preset_id?: string;
    preset_version?: string;
    seed?: number;
    song_id?: string;
    frame_count?: number;
    fps?: number;
    duration?: number;
  };
}

/**
 * Epic 01.F3: Metadata display component
 *
 * Surfaces schema version, render id, preset id, and seed in UI
 */
export const MetadataDisplay: React.FC<MetadataDisplayProps> = ({ metadata }) => {
  const durationText =
    typeof metadata.duration === 'number' ? `${metadata.duration.toFixed(2)}s` : 'Not available';

  return (
    <div
      className="metadata-display"
      style={{
        backgroundColor: '#f5f5f5',
        border: '1px solid #ddd',
        borderRadius: '4px',
        padding: '12px',
        fontFamily: 'monospace',
        fontSize: '11px',
      }}
    >
      <div style={{ marginBottom: '8px' }}>
        <strong>Schema:</strong> {metadata.schema_version ?? 'Not available'}
      </div>
      <div style={{ marginBottom: '8px', wordBreak: 'break-all' }}>
        <strong>Render ID:</strong> {metadata.render_id ?? 'Not available'}
      </div>
      <div style={{ marginBottom: '8px' }}>
        <strong>Preset:</strong>{' '}
        {metadata.preset_id ? `${metadata.preset_id} v${metadata.preset_version ?? 'unknown'}` : 'Not available'}
      </div>
      <div style={{ marginBottom: '8px' }}>
        <strong>Seed:</strong> {metadata.seed ?? 'Not available'}
      </div>
      <div style={{ marginBottom: '8px' }}>
        <strong>Song:</strong> {metadata.song_id ?? 'Not available'}
      </div>
      <div style={{ marginBottom: '8px' }}>
        <strong>Frames:</strong>{' '}
        {typeof metadata.frame_count === 'number' && typeof metadata.fps === 'number'
          ? `${metadata.frame_count} @ ${metadata.fps}fps`
          : 'Not available'}
      </div>
      <div style={{ marginBottom: '8px' }}>
        <strong>Duration:</strong> {durationText}
      </div>
    </div>
  );
};

export default MetadataDisplay;
