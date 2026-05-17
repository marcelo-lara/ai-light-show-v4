import React from 'react';
import type { DiagnosticsPanel as DiagnosticsPanelType } from '../types/phase05';

interface DiagnosticsPanelProps {
  diagnostics?: DiagnosticsPanelType;
  is_loading?: boolean;
}

/**
 * Epic 12.F2: Diagnostics Panel
 *
 * Displays diagnostics summaries and warnings in the console UI.
 */
export const DiagnosticsPanel: React.FC<DiagnosticsPanelProps> = ({ diagnostics, is_loading }) => {
  if (!diagnostics) {
    return (
      <div
        style={{
          padding: '12px',
          borderBottom: '1px solid #ddd',
          color: '#999',
          fontSize: '12px',
        }}
      >
        <h4 style={{ margin: '0 0 8px 0', fontSize: '12px', fontWeight: 'bold' }}>
          Diagnostics
        </h4>
        {is_loading ? 'Loading diagnostics...' : 'No render loaded'}
      </div>
    );
  }

  const { summary, variety, is_healthy } = diagnostics;

  const getHealthIndicator = (score: number, label: string) => {
    let color = '#f44336'; // Red - poor
    if (score > 0.7) color = '#4caf50'; // Green - good
    else if (score > 0.4) color = '#ff9800'; // Orange - fair

    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
        <div
          style={{
            width: '12px',
            height: '12px',
            backgroundColor: color,
            borderRadius: '2px',
          }}
        />
        <span style={{ fontSize: '11px' }}>
          {label}: {(score * 100).toFixed(1)}%
        </span>
      </div>
    );
  };

  return (
    <div
      style={{
        padding: '12px',
        borderBottom: '1px solid #ddd',
        backgroundColor: is_healthy ? '#f0f8f4' : '#fff3e0',
      }}
    >
      <h4 style={{ margin: '0 0 8px 0', fontSize: '12px', fontWeight: 'bold' }}>
        Diagnostics
        {is_healthy ? ' ✓' : ' ⚠'}
      </h4>

      {/* Brightness metrics */}
      <div
        style={{
          marginBottom: '8px',
          paddingBottom: '8px',
          borderBottom: '1px solid #eee',
        }}
      >
        <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '4px', color: '#333' }}>
          Brightness
        </div>
        <div style={{ fontSize: '10px', color: '#666', marginBottom: '2px' }}>
          Avg: {summary.brightness_avg.toFixed(3)} | Min: {summary.brightness_min.toFixed(3)} |
          Max: {summary.brightness_max.toFixed(3)}
        </div>
        <div style={{ fontSize: '10px', color: '#999' }}>
          Color Avg: RGB({summary.color_avg[0]}, {summary.color_avg[1]}, {summary.color_avg[2]})
        </div>
      </div>

      {/* Motion metrics */}
      <div
        style={{
          marginBottom: '8px',
          paddingBottom: '8px',
          borderBottom: '1px solid #eee',
        }}
      >
        <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '4px', color: '#333' }}>
          Motion & Variation
        </div>
        {getHealthIndicator(variety.beat_response_score, 'Beat Response')}
        {getHealthIndicator(variety.section_variation_score, 'Section Variation')}
        <div style={{ fontSize: '10px', color: '#666' }}>
          Frame Delta: {summary.frame_delta_avg.toFixed(4)}
        </div>
      </div>

      {/* Frame quality */}
      <div
        style={{
          marginBottom: '8px',
          paddingBottom: '8px',
          borderBottom: '1px solid #eee',
        }}
      >
        <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '4px', color: '#333' }}>
          Frame Quality
        </div>
        <div style={{ fontSize: '10px', color: '#666', marginBottom: '2px' }}>
          Total Frames: {summary.total_frames}
        </div>
        <div style={{ fontSize: '10px', color: summary.blank_frame_count > 0 ? '#f44336' : '#666' }}>
          Blank Frames: {summary.blank_frame_count}
        </div>
        <div style={{ fontSize: '10px', color: summary.static_frame_count > 0 ? '#ff9800' : '#666' }}>
          Static Frames: {summary.static_frame_count}
        </div>
      </div>

      {/* Warnings */}
      {variety.warnings.length > 0 && (
        <div>
          <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '4px', color: '#d32f2f' }}>
            Warnings
          </div>
          {variety.warnings.map((warning, i) => (
            <div
              key={i}
              style={{
                fontSize: '10px',
                color: '#d32f2f',
                marginBottom: '2px',
                paddingLeft: '8px',
                borderLeft: '2px solid #d32f2f',
              }}
            >
              • {warning}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DiagnosticsPanel;
