import React, { useEffect } from 'react';
import { usePlaybackStore } from '../store/playback';
import { CompatibilityError } from '../components/CompatibilityError';
import { MetadataDisplay } from '../components/MetadataDisplay';

/**
 * Main app component for Phase 1: Render Contract
 */
export const App: React.FC = () => {
  const { playbackState, compatibilityError, isLoading, loadPlaybackState, clearCompatibilityError } =
    usePlaybackStore();

  useEffect(() => {
    loadPlaybackState();
  }, [loadPlaybackState]);

  return (
    <div
      style={{
        fontFamily: 'system-ui, -apple-system, sans-serif',
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '20px',
        backgroundColor: '#fafafa',
      }}
    >
      <header style={{ marginBottom: '20px' }}>
        <h1>AI Light Show v4 - Phase 1: Render Contract</h1>
        <p style={{ color: '#666', marginTop: '8px' }}>
          Backend API: {isLoading ? 'Loading...' : 'Ready'}
        </p>
      </header>

      {/* Compatibility Error Display (Epic 01.F2) */}
      <CompatibilityError error={compatibilityError} onDismiss={clearCompatibilityError} />

      {/* Main Content */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 2fr',
          gap: '20px',
        }}
      >
        {/* Left Panel - Controls */}
        <div
          style={{
            backgroundColor: 'white',
            border: '1px solid #ddd',
            borderRadius: '4px',
            padding: '16px',
          }}
        >
          <h2 style={{ marginTop: 0 }}>Main</h2>
          <p>Show Name:</p>
          <input
            type="text"
            placeholder="Enter show name"
            style={{
              width: '100%',
              padding: '8px',
              marginBottom: '16px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              boxSizing: 'border-box',
            }}
          />
          <button
            style={{
              width: '100%',
              padding: '10px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold',
            }}
          >
            Render
          </button>
        </div>

        {/* Right Panel - Playback State & Metadata */}
        <div>
          {/* Playback State */}
          <div
            style={{
              backgroundColor: 'white',
              border: '1px solid #ddd',
              borderRadius: '4px',
              padding: '16px',
              marginBottom: '20px',
            }}
          >
            <h2 style={{ marginTop: 0 }}>Current Playback State</h2>
            <div style={{ fontFamily: 'monospace', fontSize: '12px', whiteSpace: 'pre-wrap' }}>
              {JSON.stringify(playbackState, null, 2)}
            </div>
          </div>

          {/* Metadata Display (Epic 01.F3) */}
          {playbackState?.current_song?.current_canvas?.render_artifact?.metadata && (
            <div
              style={{
                backgroundColor: 'white',
                border: '1px solid #ddd',
                borderRadius: '4px',
                padding: '16px',
              }}
            >
              <h2 style={{ marginTop: 0 }}>Render Metadata</h2>
              <MetadataDisplay
                metadata={playbackState.current_song.current_canvas.render_artifact.metadata}
              />
            </div>
          )}

          {/* Empty Canvas State (Epic 01.B6 & 01.F4) */}
          {playbackState?.current_song?.current_canvas?.is_empty && (
            <div
              style={{
                backgroundColor: '#e8f5e9',
                border: '1px solid #4caf50',
                borderRadius: '4px',
                padding: '16px',
                fontStyle: 'italic',
                color: '#2e7d32',
              }}
            >
              <strong>No render available yet.</strong> Load a song and click Render to generate a light show.
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer style={{ marginTop: '40px', paddingTop: '20px', borderTop: '1px solid #ddd', color: '#666', fontSize: '12px' }}>
        <p>Phase 1 Implementation: Render Contract - Schema v1.0</p>
      </footer>
    </div>
  );
};

export default App;
