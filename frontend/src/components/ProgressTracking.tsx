/**
 * Progress tracking UI component
 * 
 * Epic 02.B5-B9: Show render progress, phase, and status
 */

import React, { useEffect } from 'react';

export interface RenderProgressData {
  phase: 'queued' | 'analyzing' | 'rendering' | 'completed' | 'failed';
  status_text: string;
  analysis_percent?: number;
  render_percent?: number;
  overall_percent?: number;
  error_message?: string;
}

interface ProgressTrackingProps {
  progress: RenderProgressData;
  onComplete?: () => void;
  onError?: (error: string) => void;
}

/**
 * Epic 02.F20-F23: Progress bar and phase-aware UI
 */
export const ProgressTracking: React.FC<ProgressTrackingProps> = ({
  progress,
  onComplete,
  onError,
}) => {
  useEffect(() => {
    if (progress.phase === 'completed' && onComplete) {
      onComplete();
    } else if (progress.phase === 'failed' && onError && progress.error_message) {
      onError(progress.error_message);
    }
  }, [progress.phase, progress.error_message, onComplete, onError]);

  const isGenerating = progress.phase === 'analyzing' || progress.phase === 'rendering';
  const isFailed = progress.phase === 'failed';
  const isComplete = progress.phase === 'completed';

  let displayPercent = 0;
  let phaseText = '';

  if (progress.phase === 'analyzing') {
    displayPercent = progress.analysis_percent || 0;
    phaseText = 'Analyzing...';
  } else if (progress.phase === 'rendering') {
    displayPercent = progress.render_percent || 0;
    phaseText = 'Rendering...';
  } else if (progress.phase === 'completed') {
    displayPercent = 100;
    phaseText = 'Complete';
  } else if (progress.phase === 'failed') {
    phaseText = 'Failed';
  } else {
    phaseText = 'Queued';
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        padding: '12px',
        backgroundColor: '#f5f5f5',
        borderRadius: '4px',
        fontFamily: 'monospace',
        fontSize: '12px',
      }}
    >
      {/* Status header */}
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <strong>{isGenerating ? phaseText : phaseText}</strong>
        <span style={{ color: '#999' }}>{displayPercent.toFixed(0)}%</span>
      </div>

      {/* Progress bar */}
      {!isFailed && (
        <div
          style={{
            width: '100%',
            height: '20px',
            backgroundColor: '#ddd',
            borderRadius: '2px',
            overflow: 'hidden',
            position: 'relative',
          }}
        >
          <div
            style={{
              width: `${displayPercent}%`,
              height: '100%',
              backgroundColor: isComplete ? '#4caf50' : isFailed ? '#f44336' : '#2196f3',
              transition: 'width 0.3s ease',
            }}
          />
        </div>
      )}

      {/* Status text */}
      <div style={{ color: '#666', fontSize: '11px' }}>{progress.status_text}</div>

      {/* Error message */}
      {isFailed && progress.error_message && (
        <div style={{ color: '#f44336', fontSize: '11px', marginTop: '4px' }}>
          Error: {progress.error_message}
        </div>
      )}

      {/* Phase breakdown for rendering */}
      {progress.phase === 'rendering' && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '8px',
            fontSize: '10px',
            marginTop: '4px',
            paddingTop: '8px',
            borderTop: '1px solid #ddd',
          }}
        >
          <div>
            <div style={{ color: '#999' }}>Render Progress</div>
            <div>{progress.render_percent?.toFixed(0) || 0}%</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgressTracking;
