import React, { useState } from 'react';
import type { TimelineViewState, SceneInfo, TransitionInfo } from '../types/phase05';

interface TimelineViewProps {
  timeline: TimelineViewState;
  on_scene_click?: (scene_id: string) => void;
}

/**
 * Epic 02.F14: Timeline View
 *
 * Displays scene and transition metadata with visual timeline.
 */
export const TimelineView: React.FC<TimelineViewProps> = ({ timeline, on_scene_click }) => {
  const [hoveredSceneId, setHoveredSceneId] = useState<string | null>(null);

  const pixelsPerSecond = 100; // Scaling factor
  const totalWidth = Math.max(timeline.duration * pixelsPerSecond, 400);

  return (
    <div
      style={{
        padding: '12px',
        borderBottom: '1px solid #ddd',
        overflowX: 'auto',
        backgroundColor: '#f5f5f5',
      }}
    >
      <h4 style={{ marginTop: 0, marginBottom: '8px', fontSize: '12px', fontWeight: 'bold' }}>
        Timeline
      </h4>

      {/* Timeline ruler */}
      <div
        style={{
          display: 'flex',
          width: totalWidth,
          borderBottom: '1px solid #ccc',
          marginBottom: '8px',
        }}
      >
        {Array.from({ length: Math.ceil(timeline.duration) + 1 }).map((_, i) => (
          <div
            key={i}
            style={{
              width: `${pixelsPerSecond}px`,
              fontSize: '10px',
              color: '#999',
              paddingLeft: '4px',
              borderRight: '1px solid #eee',
            }}
          >
            {i}s
          </div>
        ))}
      </div>

      {/* Scenes track */}
      <div
        style={{
          display: 'flex',
          position: 'relative',
          width: totalWidth,
          height: '40px',
          backgroundColor: '#fff',
          border: '1px solid #ddd',
          marginBottom: '12px',
        }}
      >
        {timeline.scenes.map((scene) => (
          <div
            key={scene.scene_id}
            style={{
              position: 'absolute',
              left: `${scene.start_time * pixelsPerSecond}px`,
              width: `${scene.duration * pixelsPerSecond}px`,
              height: '40px',
              backgroundColor: hoveredSceneId === scene.scene_id ? '#4caf50' : '#2196f3',
              border: '1px solid #1976d2',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '10px',
              color: '#fff',
              fontWeight: 'bold',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              opacity: 0.8,
              transition: 'background-color 0.2s',
            }}
            onMouseEnter={() => setHoveredSceneId(scene.scene_id)}
            onMouseLeave={() => setHoveredSceneId(null)}
            onClick={() => on_scene_click?.(scene.scene_id)}
            title={`Scene ${scene.scene_id}: ${scene.preset_id} (${scene.start_time.toFixed(2)}s - ${(scene.start_time + scene.duration).toFixed(2)}s)`}
          >
            {scene.preset_id}
          </div>
        ))}
      </div>

      {/* Transitions track */}
      {timeline.transitions.length > 0 && (
        <div
          style={{
            display: 'flex',
            position: 'relative',
            width: totalWidth,
            height: '30px',
            backgroundColor: '#fafafa',
            border: '1px solid #ddd',
            marginBottom: '12px',
          }}
        >
          {timeline.transitions.map((transition) => (
            <div
              key={transition.transition_id}
              style={{
                position: 'absolute',
                left: `${transition.start_time * pixelsPerSecond}px`,
                width: `${transition.duration * pixelsPerSecond}px`,
                height: '30px',
                backgroundColor: '#ff9800',
                border: '1px solid #f57c00',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '9px',
                color: '#fff',
                fontWeight: 'bold',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                opacity: 0.7,
                transition: 'opacity 0.2s',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLDivElement).style.opacity = '1';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLDivElement).style.opacity = '0.7';
              }}
              title={`${transition.type} @ ${transition.start_time.toFixed(2)}s (${transition.duration.toFixed(2)}s)`}
            >
              {transition.type}
            </div>
          ))}
        </div>
      )}

      {/* Current time indicator */}
      <div style={{ fontSize: '11px', color: '#666', marginTop: '8px' }}>
        Current: {timeline.current_time.toFixed(2)}s / {timeline.duration.toFixed(2)}s
      </div>
    </div>
  );
};

export default TimelineView;
