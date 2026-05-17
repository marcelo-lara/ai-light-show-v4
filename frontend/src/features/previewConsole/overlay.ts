import type { OverlayFixture, OverlayPOI } from './types';

export const normalizeOverlayFixtures = (fixtures: Array<Record<string, unknown>>): OverlayFixture[] =>
  fixtures.flatMap((fixture) => {
    const fixtureId = typeof fixture.fixture_id === 'string'
      ? fixture.fixture_id
      : typeof fixture.id === 'string'
        ? fixture.id
        : null;

    const canvasAnchor = fixture.canvas_anchor;
    const typedCanvasAnchor =
      canvasAnchor && typeof canvasAnchor === 'object'
        ? (canvasAnchor as { x?: unknown; y?: unknown })
        : null;
    const anchorX = typeof typedCanvasAnchor?.x === 'number' ? typedCanvasAnchor.x : null;
    const anchorY = typeof typedCanvasAnchor?.y === 'number' ? typedCanvasAnchor.y : null;

    if (!fixtureId) {
      return [];
    }

    return [{
      fixture_id: fixtureId,
      canvas_anchor: anchorX !== null && anchorY !== null ? { x: anchorX, y: anchorY } : undefined,
    }];
  });

export const normalizeOverlayPOIs = (pois: Array<Record<string, unknown>>): OverlayPOI[] =>
  pois.flatMap((poi) => {
    const poiId = typeof poi.poi_id === 'string'
      ? poi.poi_id
      : typeof poi.id === 'string'
        ? poi.id
        : null;

    const canvasPos = poi.canvas_pos;
    const typedCanvasPos =
      canvasPos && typeof canvasPos === 'object'
        ? (canvasPos as { x?: unknown; y?: unknown })
        : null;
    const canvasPosX = typeof typedCanvasPos?.x === 'number' ? typedCanvasPos.x : null;
    const canvasPosY = typeof typedCanvasPos?.y === 'number' ? typedCanvasPos.y : null;

    if (!poiId || canvasPosX === null || canvasPosY === null) {
      return [];
    }

    return [{
      poi_id: poiId,
      canvas_pos: { x: canvasPosX, y: canvasPosY },
    }];
  });