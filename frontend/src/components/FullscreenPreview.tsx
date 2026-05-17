import React, { useEffect } from 'react';

interface FullscreenPreviewProps {
  is_active: boolean;
  on_exit: () => void;
  canvas_content?: React.ReactNode;
}

/**
 * Epic 02.F16: Fullscreen Preview
 *
 * Immersive fullscreen preview while preserving 100x50 character aspect ratio.
 * Exit with Escape key.
 */
export const FullscreenPreview: React.FC<FullscreenPreviewProps> = ({
  is_active,
  on_exit,
  canvas_content,
}) => {
  useEffect(() => {
    if (!is_active) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        on_exit();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [is_active, on_exit]);

  if (!is_active) {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: '#000',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
      }}
    >
      {/* Close Button */}
      <button
        onClick={on_exit}
        style={{
          position: 'absolute',
          top: '16px',
          right: '16px',
          padding: '8px 16px',
          fontSize: '14px',
          backgroundColor: '#333',
          color: '#fff',
          border: '1px solid #555',
          borderRadius: '3px',
          cursor: 'pointer',
          zIndex: 10000,
        }}
      >
        Exit Fullscreen (Esc)
      </button>

      {/* Canvas Container - centered and scaled */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '90vw',
          height: '90vh',
          maxWidth: '100vw',
          maxHeight: '100vh',
          aspectRatio: '100 / 50',
        }}
      >
        {canvas_content || (
          <div style={{ color: '#666', fontSize: '24px' }}>
            No render loaded
          </div>
        )}
      </div>

      {/* Info text */}
      <div
        style={{
          position: 'absolute',
          bottom: '16px',
          left: '16px',
          color: '#999',
          fontSize: '12px',
        }}
      >
        Press Esc to exit fullscreen
      </div>
    </div>
  );
};

export default FullscreenPreview;
