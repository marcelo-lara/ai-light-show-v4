import React from 'react';
import CanvasDisplay from '../../../components/CanvasDisplay';
import TimelineView from '../../../components/TimelineView';
import type { RenderJobStatus, TimelineViewState } from '../../../types/phase05';
import type { CurrentCanvasState } from '../../../types/renderContract';
import type { OverlayFixture, OverlayPOI } from '../types';

interface PreviewCanvasPanelProps {
  currentCanvas: CurrentCanvasState | null;
  fixtures: OverlayFixture[];
  pois: OverlayPOI[];
  frameImageUrl?: string;
  isRendering: boolean;
  renderProgress: RenderJobStatus | null;
  isPlaying?: boolean;
  onPlay: () => void;
  onPause: () => void;
  onStop: () => void;
  timeline: TimelineViewState;
}

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

export const PreviewCanvasPanel: React.FC<PreviewCanvasPanelProps> = ({
  currentCanvas,
  fixtures,
  pois,
  frameImageUrl,
  isRendering,
  renderProgress,
  isPlaying,
  onPlay,
  onPause,
  onStop,
  timeline,
}) => (
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
          fixtures={fixtures}
          pois={pois}
          frameImageUrl={frameImageUrl}
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
        onClick={onPlay}
        disabled={!currentCanvas || currentCanvas.is_empty || isPlaying}
        style={playbackButtonStyle(!currentCanvas || currentCanvas.is_empty || !!isPlaying)}
      >
        Play
      </button>
      <button
        onClick={onPause}
        disabled={!currentCanvas || currentCanvas.is_empty || !isPlaying}
        style={playbackButtonStyle(!currentCanvas || currentCanvas.is_empty || !isPlaying)}
      >
        Pause
      </button>
      <button
        onClick={onStop}
        disabled={!currentCanvas || currentCanvas.is_empty}
        style={playbackButtonStyle(!currentCanvas || currentCanvas.is_empty)}
      >
        Stop
      </button>
    </div>

    <TimelineView
      timeline={timeline}
      on_scene_click={(sceneId) => console.log('Scene clicked:', sceneId)}
    />
  </div>
);

export default PreviewCanvasPanel;