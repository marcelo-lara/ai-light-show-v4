import { useEffect, useState } from 'react';
import type { RenderArtifactMetadata } from '../../../types/renderContract';
import backendAPI from '../../../api/backend';

const MAX_PREVIEW_FPS = 12;

interface UsePreviewFrameOptions {
  metadata?: RenderArtifactMetadata;
  isPlaying?: boolean;
}

interface UsePreviewFrameResult {
  previewFrameUrl: string | null;
  resetPreviewFrame: () => void;
}

export const usePreviewFrame = ({ metadata, isPlaying }: UsePreviewFrameOptions): UsePreviewFrameResult => {
  const [previewFrameIndex, setPreviewFrameIndex] = useState(0);
  const [previewFrameUrl, setPreviewFrameUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!metadata) {
      setPreviewFrameUrl(null);
      return;
    }

    const boundedFrameIndex = metadata.frame_count > 0
      ? previewFrameIndex % metadata.frame_count
      : 0;

    setPreviewFrameUrl(backendAPI.getPresetPreviewUrl(metadata.preset_id, {
      version: metadata.preset_version,
      frameIndex: boundedFrameIndex,
      fps: metadata.fps,
      totalFrames: metadata.frame_count,
      seed: metadata.seed,
      cacheBuster: boundedFrameIndex,
    }));
  }, [metadata, previewFrameIndex]);

  useEffect(() => {
    if (!metadata || !isPlaying) {
      return;
    }

    const frameCount = Math.max(1, metadata.frame_count);
    const sourceFps = Math.max(1, metadata.fps);
    const previewFps = Math.min(sourceFps, MAX_PREVIEW_FPS);
    const tickMs = 1000 / previewFps;
    const frameStep = Math.max(1, Math.round(sourceFps / previewFps));

    const timerId = window.setInterval(() => {
      setPreviewFrameIndex((currentIndex) => (currentIndex + frameStep) % frameCount);
    }, tickMs);

    return () => window.clearInterval(timerId);
  }, [isPlaying, metadata]);

  const resetPreviewFrame = () => {
    setPreviewFrameIndex(0);
  };

  return {
    previewFrameUrl,
    resetPreviewFrame,
  };
};