import React, { useState } from 'react';
import type { ABCompareState } from '../types/phase05';

interface ABCompareProps {
  compare_state: ABCompareState;
  on_compare_toggle: () => void;
  on_split_change: (position: number) => void;
}

/**
 * Epic 02.F17: A/B Compare
 *
 * Side-by-side render comparison with split control.
 */
export const ABCompare: React.FC<ABCompareProps> = ({
  compare_state,
  on_compare_toggle,
  on_split_change,
}) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleMouseDown = () => {
    setIsDragging(true);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isDragging) return;

    const container = e.currentTarget;
    const rect = container.getBoundingClientRect();
    const position = ((e.clientX - rect.left) / rect.width) * 100;

    on_split_change(Math.max(10, Math.min(90, position)));
  };

  return (
    <div
      style={{
        padding: '12px',
        borderBottom: '1px solid #ddd',
        backgroundColor: '#f9f9f9',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h4 style={{ margin: '0 0 8px 0', fontSize: '12px', fontWeight: 'bold' }}>
          A/B Compare
        </h4>
        <button
          onClick={on_compare_toggle}
          style={{
            padding: '4px 8px',
            fontSize: '11px',
            backgroundColor: compare_state.is_comparing ? '#2196f3' : '#ccc',
            color: '#fff',
            border: 'none',
            borderRadius: '3px',
            cursor: 'pointer',
          }}
        >
          {compare_state.is_comparing ? 'ON' : 'OFF'}
        </button>
      </div>

      {compare_state.is_comparing && (
        <div
          style={{
            marginTop: '8px',
            padding: '8px',
            backgroundColor: '#fff',
            border: '1px solid #ddd',
            borderRadius: '3px',
          }}
        >
          <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '4px' }}>
                Render A
              </div>
              <div
                style={{
                  fontSize: '10px',
                  color: '#666',
                  padding: '4px',
                  backgroundColor: '#f0f0f0',
                  borderRadius: '2px',
                }}
              >
                {compare_state.render_a_id ?? 'Not selected'}
              </div>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '4px' }}>
                Render B
              </div>
              <div
                style={{
                  fontSize: '10px',
                  color: '#666',
                  padding: '4px',
                  backgroundColor: '#f0f0f0',
                  borderRadius: '2px',
                }}
              >
                {compare_state.render_b_id ?? 'Not selected'}
              </div>
            </div>
          </div>

          {/* Split Control */}
          <div style={{ marginTop: '8px' }}>
            <div style={{ fontSize: '11px', marginBottom: '4px' }}>
              Split Position: {compare_state.split_position.toFixed(1)}%
            </div>
            <div
              style={{
                height: '20px',
                backgroundColor: '#e0e0e0',
                borderRadius: '3px',
                cursor: 'col-resize',
                position: 'relative',
                overflow: 'hidden',
              }}
              onMouseDown={handleMouseDown}
              onMouseUp={handleMouseUp}
              onMouseMove={handleMouseMove}
              onMouseLeave={handleMouseUp}
            >
              <div
                style={{
                  position: 'absolute',
                  left: `${compare_state.split_position}%`,
                  width: '2px',
                  height: '100%',
                  backgroundColor: '#2196f3',
                  cursor: 'col-resize',
                }}
              />
              <div
                style={{
                  position: 'absolute',
                  left: 0,
                  width: `${compare_state.split_position}%`,
                  height: '100%',
                  backgroundColor: '#e3f2fd',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '10px',
                  fontWeight: 'bold',
                  color: '#1976d2',
                }}
              >
                A
              </div>
              <div
                style={{
                  position: 'absolute',
                  right: 0,
                  width: `${100 - compare_state.split_position}%`,
                  height: '100%',
                  backgroundColor: '#f3e5f5',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '10px',
                  fontWeight: 'bold',
                  color: '#7b1fa2',
                }}
              >
                B
              </div>
            </div>
            <div style={{ fontSize: '10px', color: '#999', marginTop: '4px' }}>
              Drag divider to adjust split position
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ABCompare;
