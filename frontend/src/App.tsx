import React, { useEffect } from 'react';
import { usePlaybackStore } from './store/playback';
import { CompatibilityError } from './components/CompatibilityError';
import CanvasDisplay from './components/CanvasDisplay';
import ControlPanel from './components/ControlPanel';
import ProgressTracking from './components/ProgressTracking';
import type { RenderArtifactMetadata } from './types/renderContract';

/**
 * Main app component for Phase 2: Preview Console
 * 
 * Epic 02: Interactive preview with canvas rendering, controls, and progress tracking
 */
export const App: React.FC = () => {
  const {
    playbackState,
    compatibilityError,
    isLoading,
    loadPlaybackState,
    clearCompatibilityError,
    loadFixtures,
    loadPOIs,
    canvasName,
    setCanvasName,
    startRender,
    renderJob,
    fixtures,
    pois,
  } = usePlaybackStore();

  useEffect(() => {
    // Load initial state and fixtures
    loadPlaybackState();
    loadFixtures();
    loadPOIs();
  }, [loadPlaybackState, loadFixtures, loadPOIs]);

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
        <div>Loading...</div>
      </div>
    );
  }

  if (compatibilityError.has_error) {
    return <CompatibilityError error={compatibilityError} onDismiss={clearCompatibilityError} />;
  }

  // Get current song
  const currentSong = playbackState?.current_song;

  // Dummy metadata for display (would come from loaded artifact)
  const dummyMetadata: RenderArtifactMetadata = {
    schema_version: '1.0',
    render_id: 'render_12345',
    render_timestamp: new Date().toISOString(),
    frame_count: 300,
    fps: 30,
    duration: 10,
    preset_id: 'preset_default',
    seed: 12345,
    compatibility_state: 'compatible',
  };

  // Control panel tabs
  const tabs = [
    { id: 'main', label: 'Main', type: 'main' as const },
    { id: 'shader1', label: 'Raindrops', type: 'shader' as const },
    { id: 'shader2', label: 'Chase', type: 'shader' as const },
  ];

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        backgroundColor: '#f0f0f0',
        fontFamily: 'system-ui, -apple-system, sans-serif',
      }}
    >
      {/* Header */}
      <div
        style={{
          backgroundColor: '#333',
          color: '#fff',
          padding: '16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '2px solid #2196f3',
        }}
      >
        <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
          AI Light Show - Preview Console
        </div>
        <div style={{ fontSize: '12px', color: '#aaa' }}>
          {currentSong ? `Song: ${currentSong.title}` : 'No song loaded'}
        </div>
      </div>

      {/* Main content grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '320px 1fr',
          gap: '16px',
          padding: '16px',
          flex: 1,
          overflow: 'hidden',
          minHeight: 0,
        }}
      >
        {/* Left panel: Controls */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
            overflow: 'auto',
            minHeight: 0,
          }}
        >
          <ControlPanel
            tabs={tabs}
            canvasNameValue={canvasName}
            onCanvasNameChange={setCanvasName}
            onRenderClick={() => startRender(canvasName)}
            isRendering={renderJob.phase === 'analyzing' || renderJob.phase === 'rendering'}
          />

          {renderJob.jobId && (
            <ProgressTracking
              progress={{
                phase: renderJob.phase as any,
                status_text: renderJob.statusText,
                render_percent: renderJob.percent,
                error_message: renderJob.errorMessage || undefined,
              }}
            />
          )}
        </div>

        {/* Right panel: Canvas display */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
            overflow: 'auto',
            backgroundColor: '#fff',
            padding: '16px',
            borderRadius: '4px',
            minHeight: 0,
          }}
        >
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#333' }}>Canvas Preview</h3>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'flex-start' }}>
              <CanvasDisplay
                metadata={dummyMetadata}
                fixtures={fixtures as any}
                pois={pois as any}
                showGrid={true}
                showOverlay={true}
                scale={6}
              />
            </div>
          </div>

          {/* Metadata display */}
          {currentSong && (
            <div
              style={{
                padding: '12px',
                backgroundColor: '#f5f5f5',
                borderRadius: '4px',
                fontSize: '11px',
                fontFamily: 'monospace',
                borderTop: '1px solid #ddd',
              }}
            >
              <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Artifact Metadata</div>
              <div>Render ID: {dummyMetadata.render_id}</div>
              <div>Schema: v{dummyMetadata.schema_version}</div>
              <div>Seed: {dummyMetadata.seed}</div>
              <div>Status: {dummyMetadata.compatibility_state}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
