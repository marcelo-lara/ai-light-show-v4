import React from 'react';
import type { RenderArtifactMetadata } from '../types/renderContract';

interface MetadataDisplayProps {
  metadata: RenderArtifactMetadata;
}

/**
 * Epic 01.F3: Metadata display component
 *
 * Surfaces schema version, render id, preset id, and seed in UI
 */
export const MetadataDisplay: React.FC<MetadataDisplayProps> = ({ metadata }) => {
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
        <strong>Schema:</strong> {metadata.schema_version}
      </div>
      <div style={{ marginBottom: '8px', wordBreak: 'break-all' }}>
        <strong>Render ID:</strong> {metadata.render_id}
      </div>
      <div style={{ marginBottom: '8px' }}>
        <strong>Preset:</strong> {metadata.preset_id} v{metadata.preset_version}
      </div>
      <div style={{ marginBottom: '8px' }}>
        <strong>Seed:</strong> {metadata.seed}
      </div>
      <div style={{ marginBottom: '8px' }}>
        <strong>Song:</strong> {metadata.song_id}
      </div>
      <div style={{ marginBottom: '8px' }}>
        <strong>Frames:</strong> {metadata.frame_count} @ {metadata.fps}fps
      </div>
      <div style={{ marginBottom: '8px' }}>
        <strong>Duration:</strong> {metadata.duration.toFixed(2)}s
      </div>
    </div>
  );
};
