import React, { useEffect, useState } from 'react';
import { usePlaybackStore } from './store/playback';
import { CompatibilityError } from './components/CompatibilityError';
import CanvasDisplay from './components/CanvasDisplay';
import MainTab from './components/MainTab';
import PresetBrowser from './components/PresetBrowser';
import TimelineView from './components/TimelineView';
import FrameInspector from './components/FrameInspector';
import DiagnosticsPanel from './components/DiagnosticsPanel';
import MetadataDisplay from './components/MetadataDisplay';
import ABCompare from './components/ABCompare';
import FullscreenPreview from './components/FullscreenPreview';
import { RenderPhase } from './types/phase05';
import type { RenderJobStatus, TimelineViewState, ABCompareState, DiagnosticsPanel as DiagnosticsPanelType } from './types/phase05';
import type { CurrentCanvasState, RenderArtifactMetadata } from './types/renderContract';
import backendAPI from './api/backend';

const MAX_PREVIEW_FPS = 12;

/**
 * Main app component for Phase 5: Production Console
 * 
 * Epic 02: Preview Console - Interactive preview, controls, and progress tracking
 * Epic 12: Render Diagnostics - Quality metrics and warnings
 */
export const App: React.FC = () => {
  const {
    playbackState,
    compatibilityError,
    isLoading,
    loadPlaybackState,
    loadSongs,
    loadSong,
    clearCompatibilityError,
    loadFixtures,
    loadPOIs,
    play,
    pause,
    stop,
    fixtures,
    pois,
    songs,
  } = usePlaybackStore();

  // Phase 05 state
  const [canvasName, setCanvasName] = useState('canvas');
  const [selectedSongId, setSelectedSongId] = useState('');
  const [selectedPresets, setSelectedPresets] = useState<Set<string>>(new Set());
  const [isRendering, setIsRendering] = useState(false);
  const [renderProgress, setRenderProgress] = useState<RenderJobStatus | null>(null);
  const [renderedCanvas, setRenderedCanvas] = useState<CurrentCanvasState | null>(null);
  const [previewFrameIndex, setPreviewFrameIndex] = useState(0);
  const [previewFrameUrl, setPreviewFrameUrl] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showFrameInspector, setShowFrameInspector] = useState(false);
  const [showDiagnostics, setShowDiagnostics] = useState(false);
  const [compareState, setCompareState] = useState<ABCompareState>({
    is_comparing: false,
    split_position: 50,
  });

  useEffect(() => {
    // Load initial state and fixtures
    loadPlaybackState();
    loadSongs();
    loadFixtures();
    loadPOIs();
  }, [loadPlaybackState, loadSongs, loadFixtures, loadPOIs]);

  useEffect(() => {
    if (playbackState?.current_song?.song_id) {
      setSelectedSongId(playbackState.current_song.song_id);
      return;
    }

    if (!selectedSongId && songs.length > 0) {
      setSelectedSongId(songs[0].id);
    }
  }, [playbackState?.current_song?.song_id, selectedSongId, songs]);

  // Get current song - Epic 02.F2: Server-owned song state
  const currentSong = playbackState?.current_song;
  const currentCanvas = renderedCanvas ?? currentSong?.current_canvas ?? null;
  const currentCanvasMetadata = currentCanvas?.render_artifact?.metadata;
  const overlayFixtures = fixtures.flatMap((fixture) => {
    const fixtureId = typeof fixture.fixture_id === 'string'
      ? fixture.fixture_id
      : typeof fixture.id === 'string'
        ? fixture.id
        : null;

    const canvasAnchor = fixture.canvas_anchor;
    const typedCanvasAnchor =
      canvasAnchor && typeof canvasAnchor === 'object'
        ? (canvasAnchor as { x?: unknown; y?: unknown })
        : null;
    const anchorX = typeof typedCanvasAnchor?.x === 'number' ? typedCanvasAnchor.x : null;
    const anchorY = typeof typedCanvasAnchor?.y === 'number' ? typedCanvasAnchor.y : null;

    if (!fixtureId) {
      return [];
    }

    return [{
      fixture_id: fixtureId,
      canvas_anchor: anchorX !== null && anchorY !== null ? { x: anchorX, y: anchorY } : undefined,
    }];
  });
  const overlayPOIs = pois.flatMap((poi) => {
    const poiId = typeof poi.poi_id === 'string'
      ? poi.poi_id
      : typeof poi.id === 'string'
        ? poi.id
        : null;

    const canvasPos = poi.canvas_pos;
    const typedCanvasPos =
      canvasPos && typeof canvasPos === 'object'
        ? (canvasPos as { x?: unknown; y?: unknown })
        : null;
    const canvasPosX = typeof typedCanvasPos?.x === 'number' ? typedCanvasPos.x : null;
    const canvasPosY = typeof typedCanvasPos?.y === 'number' ? typedCanvasPos.y : null;

    if (!poiId || canvasPosX === null || canvasPosY === null) {
      return [];
    }

    return [{
      poi_id: poiId,
      canvas_pos: { x: canvasPosX, y: canvasPosY },
    }];
  });

  // Mock available presets
  const available_presets = [
    { id: 'undersea_pulse_01', name: 'Undersea Pulse' },
    { id: 'undersea_waves', name: 'Undersea Waves' },
  ];

  const displayMetadata = currentCanvas?.render_artifact?.metadata ?? {
    song_id: currentSong?.song_id,
  };

  // Use real song duration if available, otherwise fall back to a visible placeholder
  const songDuration = currentSong?.duration ?? null;
  const halfDuration = songDuration !== null ? songDuration / 2 : 150;
  const fullDuration = songDuration ?? 300;

  useEffect(() => {
    if (!currentCanvasMetadata) {
      setPreviewFrameUrl(null);
      return;
    }

    const boundedFrameIndex = currentCanvasMetadata.frame_count > 0
      ? previewFrameIndex % currentCanvasMetadata.frame_count
      : 0;

    setPreviewFrameUrl(backendAPI.getPresetPreviewUrl(currentCanvasMetadata.preset_id, {
      version: currentCanvasMetadata.preset_version,
      frameIndex: boundedFrameIndex,
      fps: currentCanvasMetadata.fps,
      totalFrames: currentCanvasMetadata.frame_count,
      seed: currentCanvasMetadata.seed,
      cacheBuster: boundedFrameIndex,
    }));
  }, [currentCanvasMetadata, previewFrameIndex]);

  useEffect(() => {
    if (!currentCanvasMetadata || !playbackState?.is_playing) {
      return;
    }

    const frameCount = Math.max(1, currentCanvasMetadata.frame_count);
    const sourceFps = Math.max(1, currentCanvasMetadata.fps);
    const previewFps = Math.min(sourceFps, MAX_PREVIEW_FPS);
    const tickMs = 1000 / previewFps;
    const frameStep = Math.max(1, Math.round(sourceFps / previewFps));

    const timerId = window.setInterval(() => {
      setPreviewFrameIndex((currentIndex) => (currentIndex + frameStep) % frameCount);
    }, tickMs);

    return () => window.clearInterval(timerId);
  }, [currentCanvasMetadata, playbackState?.is_playing]);

  // Mock timeline
  const mockTimeline: TimelineViewState = {
    scenes: [
      { scene_id: 'scene_1', start_time: 0, duration: halfDuration, preset_id: 'undersea_pulse_01', intensity: 0.8 },
      { scene_id: 'scene_2', start_time: halfDuration, duration: halfDuration, preset_id: 'undersea_waves', intensity: 0.6 },
    ],
    transitions: [
      { transition_id: 'trans_1', type: 'crossfade', start_time: halfDuration, duration: 0.5, alignment: 'bar' },
    ],
    current_time: 0,
    duration: fullDuration,
    is_playing: false,
  };

  // Mock diagnostics
  const mockDiagnostics: DiagnosticsPanelType = {
    render_id: 'render_12345',
    summary: {
      brightness_avg: 0.5,
      brightness_min: 0.1,
      brightness_max: 0.9,
      color_avg: [128, 100, 80],
      frame_delta_avg: 0.15,
      blank_frame_count: 2,
      static_frame_count: 5,
      render_duration_ms: 500,
      total_frames: 300,
    },
    variety: {
      beat_response_score: 0.75,
      section_variation_score: 0.65,
      is_static: false,
      is_repetitive: false,
      warnings: [],
    },
    is_healthy: true,
  };

  const handleRenderStart = (params: { show_name: string; canvas_name: string; selected_presets: string[] }) => {
    setCanvasName(params.canvas_name);
    setSelectedPresets(new Set(params.selected_presets));
    setIsRendering(true);
    setRenderedCanvas(null);
    setPreviewFrameIndex(0);
    setPreviewFrameUrl(null);

    // Mock progress
    setRenderProgress({
      job_id: 'job_' + Date.now(),
      phase: RenderPhase.ANALYZING,
      status_text: 'Analyzing audio...',
      analysis_current: 0,
      analysis_total: 100,
      analysis_percent: 0,
      render_current: 0,
      render_total: 0,
      render_percent: 0,
      overall_percent: 0,
    });

    // Simulate progress
    setTimeout(() => {
      setRenderProgress((prev) => prev ? {
        ...prev,
        status_text: 'Analyzing audio...',
        analysis_current: 50,
        analysis_percent: 50,
        overall_percent: 25,
      } : null);
    }, 1000);

    setTimeout(() => {
      setRenderProgress((prev) => prev ? {
        ...prev,
        phase: RenderPhase.RENDERING,
        status_text: 'Rendering frames...',
        analysis_current: 100,
        analysis_percent: 100,
        render_total: 300,
        overall_percent: 50,
      } : null);
    }, 2000);

    setTimeout(() => {
      setRenderProgress((prev) => prev ? {
        ...prev,
        status_text: 'Rendering frames...',
        render_current: 150,
        render_percent: 50,
        overall_percent: 75,
      } : null);
    }, 3000);

    setTimeout(() => {
      setRenderProgress((prev) => prev ? {
        ...prev,
        status_text: 'Render complete',
        render_current: 300,
        render_percent: 100,
        phase: RenderPhase.COMPLETED,
        overall_percent: 100,
      } : null);
      const selectedPresetId = params.selected_presets[0] ?? 'undersea_pulse_01';
      const previewMetadata: RenderArtifactMetadata = {
        schema_version: '1.1',
        render_id: `render_${Date.now()}`,
        preset_id: selectedPresetId,
        preset_version: '1.0',
        seed: 12345,
        song_id: currentSong?.song_id ?? selectedSongId,
        analysis_id: `analysis_${Date.now()}`,
        fps: 30,
        duration: fullDuration,
        frame_count: Math.round(fullDuration * 30),
      };
      setRenderedCanvas({
        song_id: previewMetadata.song_id,
        canvas_id: params.canvas_name,
        render_artifact: {
          metadata: previewMetadata,
        },
        is_empty: false,
      });
      setPreviewFrameIndex(0);
      setIsRendering(false);
      setShowDiagnostics(true);
    }, 5000);
  };

  const handleSongLoad = async () => {
    if (!selectedSongId) {
      return;
    }

    setRenderedCanvas(null);
    setPreviewFrameIndex(0);
    setPreviewFrameUrl(null);
    setShowDiagnostics(false);
    setRenderProgress(null);
    await loadSong(selectedSongId);
  };

  const handlePlay = async () => {
    await play();
  };

  const handlePause = async () => {
    await pause();
  };

  const handleStop = async () => {
    await stop();
    setPreviewFrameIndex(0);
  };

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
      {/* Header - Epic 02.F22: Canvas name only, no song name duplication */}
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
          {currentSong ? `Song: ${currentSong.song_id}` : 'No song loaded'} | v0.5.0
        </div>
      </div>

      {/* Main content - Epic 02.F19: Full-width canvas fit */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '300px 1fr 320px',
          gap: '0',
          flex: 1,
          overflow: 'hidden',
          minHeight: 0,
        }}
      >
        {/* Left Panel: Main Tab + Preset Tabs */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            borderRight: '1px solid #ddd',
            backgroundColor: '#fff',
            overflow: 'auto',
            minHeight: 0,
          }}
        >
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
              onChange={(event) => setSelectedSongId(event.target.value)}
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
              onClick={() => void handleSongLoad()}
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

          <MainTab
            onRenderStart={handleRenderStart}
            isRendering={isRendering}
            renderProgress={renderProgress ?? undefined}
            available_presets={available_presets}
          />

          <PresetBrowser
            selected_presets={selectedPresets}
            presets={available_presets.map((p) => ({
              ...p,
              label: p.name,
              parameters: [],
            }))}
            on_preset_change={() => {}}
          />
        </div>

        {/* Center Panel: Canvas Display */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: '#1a1a1a',
            overflow: 'auto',
            minHeight: 0,
            position: 'relative',
          }}
        >
          {/* Canvas area with full-width fit */}
          <div
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '20px',
              minHeight: 0,
            }}
          >
            {currentCanvas && !currentCanvas.is_empty ? (
              <CanvasDisplay
                metadata={currentCanvas.render_artifact?.metadata}
                fixtures={overlayFixtures}
                pois={overlayPOIs}
                frameImageUrl={previewFrameUrl ?? undefined}
              />
            ) : (
              <div style={{ color: '#555', fontSize: '14px', textAlign: 'center' }}>
                {isRendering ? (
                  <div>
                    <div style={{ marginBottom: '10px' }}>Rendering...</div>
                    <div style={{ fontSize: '12px', color: '#999' }}>
                      {renderProgress?.status_text}
                    </div>
                  </div>
                ) : (
                  'Load a song and click Render to generate a show'
                )}
              </div>
            )}
          </div>

          <div
            style={{
              display: 'flex',
              gap: '8px',
              padding: '12px 20px',
              borderTop: '1px solid #333',
              justifyContent: 'center',
            }}
          >
            <button
              onClick={() => void handlePlay()}
              disabled={!currentCanvas || currentCanvas.is_empty || playbackState?.is_playing}
              style={playbackButtonStyle(!currentCanvas || currentCanvas.is_empty || !!playbackState?.is_playing)}
            >
              Play
            </button>
            <button
              onClick={() => void handlePause()}
              disabled={!currentCanvas || currentCanvas.is_empty || !playbackState?.is_playing}
              style={playbackButtonStyle(!currentCanvas || currentCanvas.is_empty || !playbackState?.is_playing)}
            >
              Pause
            </button>
            <button
              onClick={() => void handleStop()}
              disabled={!currentCanvas || currentCanvas.is_empty}
              style={playbackButtonStyle(!currentCanvas || currentCanvas.is_empty)}
            >
              Stop
            </button>
          </div>

          {/* Timeline view below canvas */}
          <TimelineView
            timeline={mockTimeline}
            on_scene_click={(scene_id) => console.log('Scene clicked:', scene_id)}
          />
        </div>

        {/* Right Panel: Metadata, Diagnostics, Frame Inspector, A/B Compare */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            borderLeft: '1px solid #ddd',
            backgroundColor: '#fff',
            overflow: 'auto',
            minHeight: 0,
          }}
        >
          <MetadataDisplay
            metadata={displayMetadata}
          />

          {showDiagnostics && (
            <DiagnosticsPanel
              diagnostics={mockDiagnostics}
              is_loading={false}
            />
          )}

          <FrameInspector
            is_active={showFrameInspector}
            on_toggle={() => setShowFrameInspector(!showFrameInspector)}
            canvas_width={100}
            canvas_height={50}
          />

          <ABCompare
            compare_state={compareState}
            on_compare_toggle={() => setCompareState({ ...compareState, is_comparing: !compareState.is_comparing })}
            on_split_change={(pos) => setCompareState({ ...compareState, split_position: pos })}
          />

          {/* Fullscreen button */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            style={{
              margin: '12px',
              padding: '8px 12px',
              fontSize: '12px',
              backgroundColor: '#2196f3',
              color: '#fff',
              border: 'none',
              borderRadius: '3px',
              cursor: 'pointer',
            }}
          >
            {isFullscreen ? '← Exit Fullscreen' : 'Fullscreen Preview →'}
          </button>
        </div>
      </div>

      {/* Fullscreen Preview - Epic 02.F16 */}
      <FullscreenPreview
        is_active={isFullscreen}
        on_exit={() => setIsFullscreen(false)}
        canvas_content={
          currentCanvas && !currentCanvas.is_empty ? (
            <CanvasDisplay
              metadata={currentCanvas.render_artifact?.metadata}
              fixtures={overlayFixtures}
              pois={overlayPOIs}
              frameImageUrl={previewFrameUrl ?? undefined}
            />
          ) : undefined
        }
      />
    </div>
  );
};

const playbackButtonStyle = (disabled: boolean): React.CSSProperties => ({
  minWidth: '84px',
  padding: '8px 14px',
  fontSize: '12px',
  fontWeight: 'bold',
  backgroundColor: disabled ? '#555' : '#2196f3',
  color: '#fff',
  border: 'none',
  borderRadius: '3px',
  cursor: disabled ? 'not-allowed' : 'pointer',
  opacity: disabled ? 0.6 : 1,
});

export default App;
