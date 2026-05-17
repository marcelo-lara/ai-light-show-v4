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
import type { RenderJobStatus, TimelineViewState, ABCompareState, ApprovalState, MetadataDisplay as MetadataDisplayType, DiagnosticsPanel as DiagnosticsPanelType } from './types/phase05';

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
    clearCompatibilityError,
    loadFixtures,
    loadPOIs,
    fixtures,
    pois,
  } = usePlaybackStore();

  // Phase 05 state
  const [activeTab, setActiveTab] = useState('main');
  const [showName, setShowName] = useState('output');
  const [canvasName, setCanvasName] = useState('canvas');
  const [selectedPresets, setSelectedPresets] = useState<Set<string>>(new Set());
  const [isRendering, setIsRendering] = useState(false);
  const [renderProgress, setRenderProgress] = useState<RenderJobStatus | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showFrameInspector, setShowFrameInspector] = useState(false);
  const [showDiagnostics, setShowDiagnostics] = useState(false);
  const [compareState, setCompareState] = useState<ABCompareState>({
    is_comparing: false,
    split_position: 50,
  });
  const [approvalState, setApprovalState] = useState<ApprovalState>({
    is_approved: false,
  });

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

  // Get current song - Epic 02.F2: Server-owned song state
  const currentSong = playbackState?.current_song;
  const currentCanvas = currentSong?.current_canvas;

  // Mock available presets
  const available_presets = [
    { id: 'undersea_pulse_01', name: 'Undersea Pulse' },
    { id: 'undersea_waves', name: 'Undersea Waves' },
  ];

  // Mock metadata
  const mockMetadata: MetadataDisplayType = {
    render_id: 'render_12345',
    schema_version: '1.1',
    preset_id: 'undersea_pulse_01',
    seed: 12345,
    compatibility_state: 'compatible',
    frame_count: 300,
    fps: 30,
    duration: 10,
    created_at: new Date().toISOString(),
  };

  // Mock timeline
  const mockTimeline: TimelineViewState = {
    scenes: [
      { scene_id: 'scene_1', start_time: 0, duration: 5, preset_id: 'undersea_pulse_01', intensity: 0.8 },
      { scene_id: 'scene_2', start_time: 5, duration: 5, preset_id: 'undersea_waves', intensity: 0.6 },
    ],
    transitions: [
      { transition_id: 'trans_1', type: 'crossfade', start_time: 5, duration: 0.5, alignment: 'bar' },
    ],
    current_time: 0,
    duration: 10,
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
    setShowName(params.show_name);
    setCanvasName(params.canvas_name);
    setSelectedPresets(new Set(params.selected_presets));
    setIsRendering(true);

    // Mock progress
    setRenderProgress({
      job_id: 'job_' + Date.now(),
      phase: 'analyzing',
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
      setRenderProgress((prev) => prev ? { ...prev, analysis_current: 50, analysis_percent: 50 } : null);
    }, 1000);

    setTimeout(() => {
      setRenderProgress((prev) => prev ? { ...prev, phase: 'rendering', analysis_current: 100, analysis_percent: 100, render_total: 300 } : null);
    }, 2000);

    setTimeout(() => {
      setRenderProgress((prev) => prev ? { ...prev, render_current: 150, render_percent: 50, overall_percent: 65 } : null);
    }, 3000);

    setTimeout(() => {
      setRenderProgress((prev) => prev ? { ...prev, render_current: 300, render_percent: 100, phase: 'completed', overall_percent: 100 } : null);
      setIsRendering(false);
      setShowDiagnostics(true);
    }, 5000);
  };

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
                artifact={currentCanvas.render_artifact}
                fixtures={fixtures}
                pois={pois}
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
            metadata={mockMetadata}
            approval={approvalState}
            on_approve={() => setApprovalState({ ...approvalState, is_approved: true })}
            on_reject={() => setApprovalState({ ...approvalState, is_approved: false })}
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
              artifact={currentCanvas.render_artifact}
              fixtures={fixtures}
              pois={pois}
            />
          ) : undefined
        }
      />
    </div>
  );
};

export default App;
            overflow: 'auto',
            minHeight: 0,
          }}
        >
          <MetadataDisplay
            metadata={mockMetadata}
            approval={approvalState}
            on_approve={() => setApprovalState({ ...approvalState, is_approved: true })}
            on_reject={() => setApprovalState({ ...approvalState, is_approved: false })}
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
              artifact={currentCanvas.render_artifact}
              fixtures={fixtures}
              pois={pois}
            />
          ) : undefined
        }
      />
    </div>
  );
};

export default App;
