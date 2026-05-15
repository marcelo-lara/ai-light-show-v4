/**
 * Canvas display and rendering component
 * 
 * Epic 02: Display the 100x50 virtual canvas with overlay
 */

import React, { useEffect, useState } from 'react';
import type { RenderArtifactMetadata } from '../types/renderContract';

interface CanvasDisplayProps {
  metadata?: RenderArtifactMetadata;
  fixtures?: Array<{ fixture_id: string; canvas_anchor?: { x: number; y: number } }>;
  pois?: Array<{ poi_id: string; canvas_pos: { x: number; y: number } }>;
  showGrid?: boolean;
  showOverlay?: boolean;
  scale?: number;
}

/**
 * Epic 02.F19: Full-width canvas that preserves 100x50 aspect ratio
 */
export const CanvasDisplay: React.FC<CanvasDisplayProps> = ({
  metadata,
  fixtures = [],
  pois = [],
  showGrid = true,
  showOverlay = true,
  scale = 8,
}) => {
  const CANVAS_WIDTH = 100;
  const CANVAS_HEIGHT = 50;
  const displayWidth = CANVAS_WIDTH * scale;
  const displayHeight = CANVAS_HEIGHT * scale;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
      }}
    >
      {/* Metadata info */}
      {metadata && (
        <div
          style={{
            fontSize: '12px',
            color: '#666',
            fontFamily: 'monospace',
          }}
        >
          <div>Canvas: {CANVAS_WIDTH}x{CANVAS_HEIGHT} @ {metadata.fps}fps</div>
          <div>{metadata.frame_count} frames ({metadata.duration.toFixed(2)}s)</div>
        </div>
      )}

      {/* Canvas container */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          aspectRatio: `${CANVAS_WIDTH} / ${CANVAS_HEIGHT}`,
          backgroundColor: '#000',
          border: '2px solid #333',
          borderRadius: '4px',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Canvas background (placeholder) */}
        <div
          style={{
            width: '100%',
            height: '100%',
            position: 'relative',
            backgroundColor: '#111',
          }}
        >
          {/* Grid overlay */}
          {showGrid && (
            <svg
              style={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                pointerEvents: 'none',
              }}
            >
              {/* Vertical grid lines every 10 units */}
              {Array.from({ length: CANVAS_WIDTH / 10 + 1 }).map((_, i) => (
                <line
                  key={`vline-${i}`}
                  x1={`${(i / CANVAS_WIDTH) * 100}%`}
                  y1="0%"
                  x2={`${(i / CANVAS_WIDTH) * 100}%`}
                  y2="100%"
                  stroke="#333"
                  strokeWidth="1"
                />
              ))}
              {/* Horizontal grid lines every 10 units */}
              {Array.from({ length: CANVAS_HEIGHT / 10 + 1 }).map((_, i) => (
                <line
                  key={`hline-${i}`}
                  x1="0%"
                  y1={`${(i / CANVAS_HEIGHT) * 100}%`}
                  x2="100%"
                  y2={`${(i / CANVAS_HEIGHT) * 100}%`}
                  stroke="#333"
                  strokeWidth="1"
                />
              ))}
            </svg>
          )}

          {/* POI overlay (green circles) */}
          {showOverlay && (
            <svg style={{ position: 'absolute', width: '100%', height: '100%', pointerEvents: 'none' }}>
              {pois.map((poi) => (
                <circle
                  key={poi.poi_id}
                  cx={`${(poi.canvas_pos.x / CANVAS_WIDTH) * 100}%`}
                  cy={`${(poi.canvas_pos.y / CANVAS_HEIGHT) * 100}%`}
                  r="2%"
                  fill="none"
                  stroke="#0f0"
                  strokeWidth="2"
                />
              ))}
            </svg>
          )}

          {/* Fixture overlay (red squares) */}
          {showOverlay && (
            <svg style={{ position: 'absolute', width: '100%', height: '100%', pointerEvents: 'none' }}>
              {fixtures.map((fixture) => {
                const anchor = fixture.canvas_anchor;
                if (!anchor) return null;
                return (
                  <rect
                    key={fixture.fixture_id}
                    x={`calc(${(anchor.x / CANVAS_WIDTH) * 100}% - 1.5%)`}
                    y={`calc(${(anchor.y / CANVAS_HEIGHT) * 100}% - 1.5%)`}
                    width="3%"
                    height="3%"
                    fill="#f00"
                  />
                );
              })}
            </svg>
          )}

          {/* Center origin marker */}
          <svg style={{ position: 'absolute', width: '100%', height: '100%', pointerEvents: 'none' }}>
            <circle cx="50%" cy="50%" r="1%" fill="none" stroke="#fff" strokeWidth="1" strokeDasharray="5,5" />
          </svg>
        </div>
      </div>

      {/* Legend */}
      {showOverlay && (
        <div style={{ fontSize: '11px', color: '#999', fontFamily: 'monospace', display: 'flex', gap: '20px' }}>
          <div>
            <span style={{ color: '#0f0' }}>●</span> POI
          </div>
          <div>
            <span style={{ color: '#f00' }}>■</span> Fixture
          </div>
        </div>
      )}
    </div>
  );
};

export default CanvasDisplay;
