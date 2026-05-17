import React, { useState } from 'react';
import { usePlaybackStore } from './store/playback';
import { CompatibilityError } from './components/CompatibilityError';
import CanvasDisplay from './components/CanvasDisplay';
import MainTab from './components/MainTab';
import PresetBrowser from './components/PresetBrowser';
import FullscreenPreview from './components/FullscreenPreview';
import type { ABCompareState } from './types/phase05';
import { PreviewHeader } from './features/previewConsole/components/PreviewHeader';
import { SongLoadPanel } from './features/previewConsole/components/SongLoadPanel';
import { PreviewCanvasPanel } from './features/previewConsole/components/PreviewCanvasPanel';
import { PreviewSidebar } from './features/previewConsole/components/PreviewSidebar';
import { usePreviewConsoleBootstrap } from './features/previewConsole/hooks/usePreviewConsoleBootstrap';
import { usePreviewFrame } from './features/previewConsole/hooks/usePreviewFrame';
import { useRenderSimulation } from './features/previewConsole/hooks/useRenderSimulation';
import { AVAILABLE_PRESETS, DEFAULT_COMPARE_STATE, createMockTimeline, MOCK_DIAGNOSTICS } from './features/previewConsole/mockData';
import { normalizeOverlayFixtures, normalizeOverlayPOIs } from './features/previewConsole/overlay';
import type { RenderStartParams } from './features/previewConsole/types';

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
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showFrameInspector, setShowFrameInspector] = useState(false);
  const [compareState, setCompareState] = useState<ABCompareState>(DEFAULT_COMPARE_STATE);

  usePreviewConsoleBootstrap({
    loadPlaybackState,
    loadSongs,
    loadFixtures,
    loadPOIs,
    playbackSongId: playbackState?.current_song?.song_id,
    selectedSongId,
    setSelectedSongId,
    songs,
  });

  // Get current song - Epic 02.F2: Server-owned song state
  const currentSong = playbackState?.current_song;
  const songDuration = currentSong?.duration ?? null;
  const halfDuration = songDuration !== null ? songDuration / 2 : 150;
  const fullDuration = songDuration ?? 300;
  const {
    isRendering,
    renderProgress,
    renderedCanvas,
    showDiagnostics,
    startRender,
    resetRenderState,
  } = useRenderSimulation({
    currentSongId: currentSong?.song_id,
    selectedSongId,
    fullDuration,
  });
  const currentCanvas = renderedCanvas ?? currentSong?.current_canvas ?? null;
  const currentCanvasMetadata = currentCanvas?.render_artifact?.metadata;
  const overlayFixtures = normalizeOverlayFixtures(fixtures);
  const overlayPOIs = normalizeOverlayPOIs(pois);

  const displayMetadata = currentCanvas?.render_artifact?.metadata ?? {
    song_id: currentSong?.song_id,
  };
  const previewTimeline = createMockTimeline(halfDuration, fullDuration);
  const { previewFrameUrl, resetPreviewFrame } = usePreviewFrame({
    metadata: currentCanvasMetadata,
    isPlaying: playbackState?.is_playing,
  });

  const handleRenderStart = (params: RenderStartParams) => {
    setCanvasName(params.canvas_name);
    setSelectedPresets(new Set(params.selected_presets));
    resetPreviewFrame();
    startRender(params);
  };

  const handleSongLoad = async () => {
    if (!selectedSongId) {
      return;
    }

    resetPreviewFrame();
    resetRenderState();
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
    resetPreviewFrame();
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
      <PreviewHeader canvasName={canvasName} currentSongId={currentSong?.song_id} />

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
          <SongLoadPanel
            selectedSongId={selectedSongId}
            songs={songs}
            onSongChange={setSelectedSongId}
            onLoadSong={() => void handleSongLoad()}
          />

          <MainTab
            onRenderStart={handleRenderStart}
            isRendering={isRendering}
            renderProgress={renderProgress ?? undefined}
            available_presets={AVAILABLE_PRESETS}
          />

          <PresetBrowser
            selected_presets={selectedPresets}
            presets={AVAILABLE_PRESETS.map((preset) => ({
              ...preset,
              label: preset.name,
              parameters: [],
            }))}
            on_preset_change={() => {}}
          />
        </div>

        <PreviewCanvasPanel
          currentCanvas={currentCanvas}
          fixtures={overlayFixtures}
          pois={overlayPOIs}
          frameImageUrl={previewFrameUrl ?? undefined}
          isRendering={isRendering}
          renderProgress={renderProgress}
          isPlaying={playbackState?.is_playing}
          onPlay={() => void handlePlay()}
          onPause={() => void handlePause()}
          onStop={() => void handleStop()}
          timeline={previewTimeline}
        />

        <PreviewSidebar
          metadata={displayMetadata}
          showDiagnostics={showDiagnostics}
          diagnostics={MOCK_DIAGNOSTICS}
          showFrameInspector={showFrameInspector}
          onToggleFrameInspector={() => setShowFrameInspector(!showFrameInspector)}
          compareState={compareState}
          onToggleCompare={() => setCompareState({ ...compareState, is_comparing: !compareState.is_comparing })}
          onSplitChange={(position: number) => setCompareState({ ...compareState, split_position: position })}
          isFullscreen={isFullscreen}
          onToggleFullscreen={() => setIsFullscreen(!isFullscreen)}
        />
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

export default App;
