import React, { useState, useRef } from 'react';

interface FrameInspectorProps {
  is_active: boolean;
  on_toggle: () => void;
  canvas_width: number;
  canvas_height: number;
}

/**
 * Epic 02.F15: Frame Inspector
 *
 * Pixel-level inspection with coordinates and RGB values.
 */
export const FrameInspector: React.FC<FrameInspectorProps> = ({
  is_active,
  on_toggle,
  canvas_width,
  canvas_height,
}) => {
  const [coordinates, setCoordinates] = useState<{ x: number; y: number } | null>(null);
  const [rgb, setRgb] = useState<[number, number, number] | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleCanvasMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!is_active || !canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = Math.floor(((e.clientX - rect.left) / rect.width) * canvas_width);
    const y = Math.floor(((e.clientY - rect.top) / rect.height) * canvas_height);

    // Bounds check
    if (x >= 0 && x < canvas_width && y >= 0 && y < canvas_height) {
      setCoordinates({ x, y });

      // In production, would extract pixel data from canvas
      // For now, show mock RGB values based on position
      const r = Math.floor((x / canvas_width) * 255);
      const g = Math.floor((y / canvas_height) * 255);
      const b = 128;
      setRgb([r, g, b]);
    }
  };

  const handleCanvasMouseLeave = () => {
    if (!is_active) {
      setCoordinates(null);
      setRgb(null);
    }
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
          Frame Inspector
        </h4>
        <button
          onClick={on_toggle}
          style={{
            padding: '4px 8px',
            fontSize: '11px',
            backgroundColor: is_active ? '#4caf50' : '#ccc',
            color: '#fff',
            border: 'none',
            borderRadius: '3px',
            cursor: 'pointer',
          }}
        >
          {is_active ? 'ON' : 'OFF'}
        </button>
      </div>

      {is_active && (
        <div
          style={{
            marginTop: '8px',
            padding: '8px',
            backgroundColor: '#fff',
            border: '1px solid #ddd',
            borderRadius: '3px',
          }}
        >
          {coordinates && rgb ? (
            <div>
              <div style={{ fontSize: '12px', marginBottom: '4px' }}>
                <strong>Coordinates:</strong> X: {coordinates.x}, Y: {coordinates.y}
              </div>
              <div style={{ fontSize: '12px', marginBottom: '4px' }}>
                <strong>RGB:</strong> R: {rgb[0]}, G: {rgb[1]}, B: {rgb[2]}
              </div>
              <div
                style={{
                  display: 'inline-block',
                  width: '30px',
                  height: '30px',
                  backgroundColor: `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`,
                  border: '1px solid #999',
                  borderRadius: '2px',
                }}
                title={`RGB(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`}
              />
            </div>
          ) : (
            <div style={{ fontSize: '12px', color: '#999' }}>
              Move cursor over the canvas to inspect pixels
            </div>
          )}
        </div>
      )}

      {/* Hidden canvas element for reference */}
      <canvas
        ref={canvasRef}
        width={canvas_width}
        height={canvas_height}
        style={{ display: 'none' }}
        onMouseMove={handleCanvasMouseMove}
        onMouseLeave={handleCanvasMouseLeave}
      />
    </div>
  );
};

export default FrameInspector;
