/**
 * Control panel UI with tabs
 * 
 * Epic 02.F5-F6: Main tab + shader parameter tabs
 */

import React, { useState } from 'react';

interface TabConfig {
  id: string;
  label: string;
  type: 'main' | 'shader' | 'layer';
}

interface ControlPanelProps {
  tabs: TabConfig[];
  onCanvasNameChange?: (name: string) => void;
  onRenderClick?: () => void;
  canvasNameValue?: string;
  isRendering?: boolean;
}

/**
 * Epic 02.F5: Main tab with show name and Render button
 * Epic 02.F6: Shader tabs for layer parameters
 */
export const ControlPanel: React.FC<ControlPanelProps> = ({
  tabs,
  onCanvasNameChange,
  onRenderClick,
  canvasNameValue = 'default',
  isRendering = false,
}) => {
  const [activeTabId, setActiveTabId] = useState(tabs[0]?.id || 'main');

  const activeTab = tabs.find((t) => t.id === activeTabId);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        backgroundColor: '#fff',
        border: '1px solid #ddd',
        borderRadius: '4px',
        overflow: 'hidden',
      }}
    >
      {/* Tab buttons */}
      <div
        style={{
          display: 'flex',
          borderBottom: '1px solid #ddd',
          backgroundColor: '#f9f9f9',
          overflowX: 'auto',
        }}
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTabId(tab.id)}
            style={{
              flex: '0 0 auto',
              padding: '10px 16px',
              border: 'none',
              backgroundColor: activeTabId === tab.id ? '#fff' : '#f9f9f9',
              borderBottom: activeTabId === tab.id ? '3px solid #2196f3' : 'none',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: activeTabId === tab.id ? 'bold' : 'normal',
              color: activeTabId === tab.id ? '#2196f3' : '#666',
              whiteSpace: 'nowrap',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '16px',
        }}
      >
        {activeTab?.type === 'main' && (
          <MainTabContent
            canvasNameValue={canvasNameValue}
            onCanvasNameChange={onCanvasNameChange}
            onRenderClick={onRenderClick}
            isRendering={isRendering}
          />
        )}
        {activeTab?.type === 'shader' && <ShaderTabContent label={activeTab.label} />}
        {activeTab?.type === 'layer' && <LayerTabContent label={activeTab.label} />}
      </div>
    </div>
  );
};

interface MainTabContentProps {
  canvasNameValue: string;
  onCanvasNameChange?: (name: string) => void;
  onRenderClick?: () => void;
  isRendering?: boolean;
}

const MainTabContent: React.FC<MainTabContentProps> = ({
  canvasNameValue,
  onCanvasNameChange,
  onRenderClick,
  isRendering,
}) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
    <div>
      <label
        style={{
          display: 'block',
          fontSize: '12px',
          fontWeight: 'bold',
          marginBottom: '6px',
          color: '#333',
        }}
      >
        Canvas Name
      </label>
      <input
        type="text"
        value={canvasNameValue}
        onChange={(e) => onCanvasNameChange?.(e.target.value)}
        style={{
          width: '100%',
          padding: '8px',
          border: '1px solid #ddd',
          borderRadius: '2px',
          fontFamily: 'monospace',
          fontSize: '12px',
          boxSizing: 'border-box',
        }}
        placeholder="canvas_name"
        disabled={isRendering}
      />
    </div>

    <button
      onClick={onRenderClick}
      disabled={isRendering}
      style={{
        padding: '12px',
        backgroundColor: isRendering ? '#ccc' : '#2196f3',
        color: '#fff',
        border: 'none',
        borderRadius: '4px',
        fontWeight: 'bold',
        cursor: isRendering ? 'not-allowed' : 'pointer',
        fontSize: '14px',
      }}
    >
      {isRendering ? 'Rendering...' : 'Render'}
    </button>
  </div>
);

interface ShaderTabContentProps {
  label: string;
}

const ShaderTabContent: React.FC<ShaderTabContentProps> = ({ label }) => (
  <div style={{ color: '#999', fontSize: '12px' }}>
    <p>
      <strong>{label} Parameters</strong>
    </p>
    <p>Shader configuration will appear here once presets are loaded.</p>
  </div>
);

interface LayerTabContentProps {
  label: string;
}

const LayerTabContent: React.FC<LayerTabContentProps> = ({ label }) => (
  <div style={{ color: '#999', fontSize: '12px' }}>
    <p>
      <strong>{label} Parameters</strong>
    </p>
    <p>Layer configuration will appear here once presets are loaded.</p>
  </div>
);

export default ControlPanel;
