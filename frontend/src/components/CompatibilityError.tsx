import React from 'react';
import type { CompatibilityErrorState } from '../types/renderContract';

interface CompatibilityErrorProps {
  error: CompatibilityErrorState;
  onDismiss?: () => void;
}

export const CompatibilityError: React.FC<CompatibilityErrorProps> = ({ error, onDismiss }) => {
  if (!error.has_error) {
    return null;
  }

  return (
    <div
      className="compatibility-error-container"
      role="alert"
      style={{
        backgroundColor: '#fee',
        border: '1px solid #fcc',
        borderRadius: '4px',
        padding: '16px',
        marginBottom: '16px',
        fontFamily: 'monospace',
        fontSize: '12px',
      }}
    >
      <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
        Render Artifact Incompatible
      </div>
      <div style={{ marginBottom: '8px' }}>{error.error_message}</div>
      {error.incompatible_render_id && (
        <div style={{ marginBottom: '8px', opacity: 0.7 }}>
          Render ID: {error.incompatible_render_id}
        </div>
      )}
      {error.suggested_action && (
        <div style={{ marginBottom: '8px', fontStyle: 'italic' }}>
          Action: {error.suggested_action}
        </div>
      )}
      {onDismiss && (
        <button
          onClick={onDismiss}
          style={{
            padding: '4px 12px',
            backgroundColor: '#fcc',
            border: '1px solid #f99',
            borderRadius: '2px',
            cursor: 'pointer',
          }}
        >
          Dismiss
        </button>
      )}
    </div>
  );
};
