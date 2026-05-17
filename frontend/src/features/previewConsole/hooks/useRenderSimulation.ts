import { useEffect, useRef, useState } from 'react';
import { RenderPhase } from '../../../types/phase05';
import type { RenderJobStatus } from '../../../types/phase05';
import type { CurrentCanvasState, RenderArtifactMetadata } from '../../../types/renderContract';
import type { RenderStartParams } from '../types';

interface UseRenderSimulationOptions {
  currentSongId?: string;
  selectedSongId: string;
  fullDuration: number;
}

interface UseRenderSimulationResult {
  isRendering: boolean;
  renderProgress: RenderJobStatus | null;
  renderedCanvas: CurrentCanvasState | null;
  showDiagnostics: boolean;
  startRender: (params: RenderStartParams) => void;
  resetRenderState: () => void;
}

export const useRenderSimulation = ({
  currentSongId,
  selectedSongId,
  fullDuration,
}: UseRenderSimulationOptions): UseRenderSimulationResult => {
  const [isRendering, setIsRendering] = useState(false);
  const [renderProgress, setRenderProgress] = useState<RenderJobStatus | null>(null);
  const [renderedCanvas, setRenderedCanvas] = useState<CurrentCanvasState | null>(null);
  const [showDiagnostics, setShowDiagnostics] = useState(false);
  const timerIdsRef = useRef<number[]>([]);

  const clearTimers = () => {
    timerIdsRef.current.forEach((timerId) => window.clearTimeout(timerId));
    timerIdsRef.current = [];
  };

  const scheduleStep = (callback: () => void, delayMs: number) => {
    const timerId = window.setTimeout(callback, delayMs);
    timerIdsRef.current.push(timerId);
  };

  const resetRenderState = () => {
    clearTimers();
    setIsRendering(false);
    setRenderProgress(null);
    setRenderedCanvas(null);
    setShowDiagnostics(false);
  };

  useEffect(() => () => clearTimers(), []);

  const startRender = (params: RenderStartParams) => {
    clearTimers();
    setIsRendering(true);
    setRenderedCanvas(null);
    setShowDiagnostics(false);

    setRenderProgress({
      job_id: `job_${Date.now()}`,
      phase: RenderPhase.ANALYZING,
      status_text: 'Analyzing audio...',
      analysis_current: 0,
      analysis_total: 100,
      analysis_percent: 0,
      render_current: 0,
      render_total: 0,
      render_percent: 0,
      overall_percent: 0,
    });

    scheduleStep(() => {
      setRenderProgress((prev) => prev ? {
        ...prev,
        status_text: 'Analyzing audio...',
        analysis_current: 50,
        analysis_percent: 50,
        overall_percent: 25,
      } : null);
    }, 1000);

    scheduleStep(() => {
      setRenderProgress((prev) => prev ? {
        ...prev,
        phase: RenderPhase.RENDERING,
        status_text: 'Rendering frames...',
        analysis_current: 100,
        analysis_percent: 100,
        render_total: 300,
        overall_percent: 50,
      } : null);
    }, 2000);

    scheduleStep(() => {
      setRenderProgress((prev) => prev ? {
        ...prev,
        status_text: 'Rendering frames...',
        render_current: 150,
        render_percent: 50,
        overall_percent: 75,
      } : null);
    }, 3000);

    scheduleStep(() => {
      setRenderProgress((prev) => prev ? {
        ...prev,
        status_text: 'Render complete',
        render_current: 300,
        render_percent: 100,
        phase: RenderPhase.COMPLETED,
        overall_percent: 100,
      } : null);

      const selectedPresetId = params.selected_presets[0] ?? 'undersea_pulse_01';
      const previewMetadata: RenderArtifactMetadata = {
        schema_version: '1.1',
        render_id: `render_${Date.now()}`,
        preset_id: selectedPresetId,
        preset_version: '1.0',
        seed: 12345,
        song_id: currentSongId ?? selectedSongId,
        analysis_id: `analysis_${Date.now()}`,
        fps: 30,
        duration: fullDuration,
        frame_count: Math.round(fullDuration * 30),
      };

      setRenderedCanvas({
        song_id: previewMetadata.song_id,
        canvas_id: params.canvas_name,
        render_artifact: {
          metadata: previewMetadata,
        },
        is_empty: false,
      });
      setIsRendering(false);
      setShowDiagnostics(true);
    }, 5000);
  };

  return {
    isRendering,
    renderProgress,
    renderedCanvas,
    showDiagnostics,
    startRender,
    resetRenderState,
  };
};