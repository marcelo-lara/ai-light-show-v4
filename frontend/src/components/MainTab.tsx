import React, { useState } from 'react';
import type { MainTabState, RenderJobStatus } from '../types/phase05';

interface MainTabProps {
  onRenderStart: (params: { show_name: string; canvas_name: string; selected_presets: string[] }) => void;
  isRendering: boolean;
  renderProgress?: RenderJobStatus;
  available_presets: Array<{ id: string; name: string }>;
}

/**
 * Epic 02.F5, 02.F24, 02.F21, 02.F22: Main Tab
 *
 * Contains show name input, canvas name input, preset checklist, and render button.
 * Default mode is overwrite.
 */
export const MainTab: React.FC<MainTabProps> = ({
  onRenderStart,
  isRendering,
  renderProgress,
  available_presets,
}) => {
  const [showName, setShowName] = useState('output');
  const [canvasName, setCanvasName] = useState('canvas');
  const [selectedPresets, setSelectedPresets] = useState<Set<string>>(new Set());

  const handlePresetToggle = (presetId: string) => {
    const newSelected = new Set(selectedPresets);
    if (newSelected.has(presetId)) {
      newSelected.delete(presetId);
    } else {
      newSelected.add(presetId);
    }
    setSelectedPresets(newSelected);
  };

  const handleRender = () => {
    if (selectedPresets.size === 0 && available_presets.length > 0) {
      alert('Please select at least one preset');
      return;
    }

    onRenderStart({
      show_name: showName,
      canvas_name: canvasName,
      selected_presets: Array.from(selectedPresets),
    });
  };

  const progressPercent = renderProgress?.overall_percent ?? 0;

  return (
    <div style={{ padding: '16px', borderBottom: '1px solid #ccc' }}>
      <h3 style={{ marginTop: 0, marginBottom: '12px', fontSize: '14px', fontWeight: 'bold' }}>
        Main
      </h3>

      {/* Show Name Input */}
      <div style={{ marginBottom: '12px' }}>
        <label
          style={{
            display: 'block',
            marginBottom: '4px',
            fontSize: '12px',
            fontWeight: 'bold',
          }}
        >
          Show Name (Overwrite Mode):
        </label>
        <input
          type="text"
          value={showName}
          onChange={(e) => setShowName(e.target.value)}
          style={{
            width: '100%',
            padding: '6px',
            fontSize: '12px',
            border: '1px solid #999',
            borderRadius: '3px',
            boxSizing: 'border-box',
          }}
          placeholder="output"
        />
      </div>

      {/* Canvas Name Input */}
      <div style={{ marginBottom: '12px' }}>
        <label
          style={{
            display: 'block',
            marginBottom: '4px',
            fontSize: '12px',
            fontWeight: 'bold',
          }}
        >
          Canvas Name:
        </label>
        <input
          type="text"
          value={canvasName}
          onChange={(e) => setCanvasName(e.target.value)}
          style={{
            width: '100%',
            padding: '6px',
            fontSize: '12px',
            border: '1px solid #999',
            borderRadius: '3px',
            boxSizing: 'border-box',
          }}
          placeholder="canvas"
        />
        <div style={{ fontSize: '11px', color: '#666', marginTop: '4px' }}>
          Export: {showName}.{canvasName}.json
        </div>
      </div>

      {/* Preset Checklist */}
      <div style={{ marginBottom: '12px' }}>
        <label
          style={{
            display: 'block',
            marginBottom: '8px',
            fontSize: '12px',
            fontWeight: 'bold',
          }}
        >
          Presets to Include:
        </label>
        <div
          style={{
            border: '1px solid #ddd',
            borderRadius: '3px',
            backgroundColor: '#fafafa',
            maxHeight: '150px',
            overflowY: 'auto',
            padding: '8px',
          }}
        >
          {available_presets.length === 0 ? (
            <div style={{ fontSize: '12px', color: '#999' }}>No presets available</div>
          ) : (
            available_presets.map((preset) => (
              <label
                key={preset.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  marginBottom: '6px',
                  fontSize: '12px',
                  cursor: 'pointer',
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedPresets.has(preset.id)}
                  onChange={() => handlePresetToggle(preset.id)}
                  style={{ marginRight: '8px' }}
                />
                {preset.name}
              </label>
            ))
          )}
        </div>
      </div>

      {/* Render Button & Progress */}
      <button
        onClick={handleRender}
        disabled={isRendering}
        style={{
          width: '100%',
          padding: '10px',
          fontSize: '14px',
          fontWeight: 'bold',
          backgroundColor: isRendering ? '#ccc' : '#2196f3',
          color: '#fff',
          border: 'none',
          borderRadius: '3px',
          cursor: isRendering ? 'not-allowed' : 'pointer',
          marginBottom: '8px',
        }}
      >
        {isRendering ? 'Rendering...' : 'Render'}
      </button>

      {/* Progress Bar */}
      {renderProgress && (
        <div style={{ marginTop: '12px' }}>
          <div
            style={{
              width: '100%',
              height: '4px',
              backgroundColor: '#e0e0e0',
              borderRadius: '2px',
              overflow: 'hidden',
              marginBottom: '4px',
            }}
          >
            <div
              style={{
                height: '100%',
                width: `${progressPercent}%`,
                backgroundColor: '#4caf50',
                transition: 'width 0.3s ease',
              }}
            />
          </div>
          <div style={{ fontSize: '11px', color: '#666' }}>
            {renderProgress.status_text} ({progressPercent.toFixed(1)}%)
          </div>
          {renderProgress.phase === 'analyzing' && (
            <div style={{ fontSize: '11px', color: '#999', marginTop: '2px' }}>
              Analysis: {renderProgress.analysis_current}/{renderProgress.analysis_total}
            </div>
          )}
          {renderProgress.phase === 'rendering' && (
            <div style={{ fontSize: '11px', color: '#999', marginTop: '2px' }}>
              Frames: {renderProgress.render_current}/{renderProgress.render_total}
            </div>
          )}
          {renderProgress.error_message && (
            <div style={{ fontSize: '11px', color: '#f44336', marginTop: '4px' }}>
              Error: {renderProgress.error_message}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MainTab;
