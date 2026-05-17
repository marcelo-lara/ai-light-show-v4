import React from 'react';
import FrameInspector from '../../../components/FrameInspector';
import DiagnosticsPanel from '../../../components/DiagnosticsPanel';
import MetadataDisplay from '../../../components/MetadataDisplay';
import ABCompare from '../../../components/ABCompare';
import type { ABCompareState, DiagnosticsPanel as DiagnosticsPanelType } from '../../../types/phase05';
import type { RenderArtifactMetadata } from '../../../types/renderContract';

interface PreviewSidebarProps {
  metadata: Partial<RenderArtifactMetadata>;
  showDiagnostics: boolean;
  diagnostics: DiagnosticsPanelType;
  showFrameInspector: boolean;
  onToggleFrameInspector: () => void;
  compareState: ABCompareState;
  onToggleCompare: () => void;
  onSplitChange: (position: number) => void;
  isFullscreen: boolean;
  onToggleFullscreen: () => void;
}

export const PreviewSidebar: React.FC<PreviewSidebarProps> = ({
  metadata,
  showDiagnostics,
  diagnostics,
  showFrameInspector,
  onToggleFrameInspector,
  compareState,
  onToggleCompare,
  onSplitChange,
  isFullscreen,
  onToggleFullscreen,
}) => (
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
    <MetadataDisplay metadata={metadata} />

    {showDiagnostics && (
      <DiagnosticsPanel
        diagnostics={diagnostics}
        is_loading={false}
      />
    )}

    <FrameInspector
      is_active={showFrameInspector}
      on_toggle={onToggleFrameInspector}
      canvas_width={100}
      canvas_height={50}
    />

    <ABCompare
      compare_state={compareState}
      on_compare_toggle={onToggleCompare}
      on_split_change={onSplitChange}
    />

    <button
      onClick={onToggleFullscreen}
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
);

export default PreviewSidebar;