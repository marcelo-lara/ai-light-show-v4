"""
Phase 06 Frontend Types

Epic 11 & 12 frontend type definitions for export and fixture mapping
"""

export interface CanonicalPixelInfo {
  origin: string;
  width: number;
  height: number;
  totalPixels: number;
  pixelOrder: string;
}

export interface FixtureReference {
  id: string;
  name: string;
  fixture: string;
  baseChannel: number;
  location: {
    x: number;
    y: number;
    z: number;
  };
}

export interface POIReference {
  id: string;
  name: string;
  location: {
    x: number;
    y: number;
    z: number;
  };
  fixtures?: Record<string, {
    pan: number;
    tilt: number;
  }>;
}

export interface FixtureMapping {
  mappingId: string;
  fixtureId: string;
  fixtureType: string;
  canvasAnchorX: number;
  canvasAnchorY: number;
  pixelWidth: number;
  pixelHeight: number;
  mappingType: 'linear' | 'serpentine' | 'custom';
  reverseX?: boolean;
  reverseY?: boolean;
  calibrationPoiId?: string;
}

export interface ExportMetadata {
  mappingId: string;
  fixtureId: string;
  fixtureType: string;
  pixelCount: number;
  mappingType: string;
}

export interface GammaCorrectionConfig {
  enabled: boolean;
  gamma: number;
}

export interface BrightnessLimitingConfig {
  enabled: boolean;
  maxBrightness: number;
}

export interface ExportManifest {
  manifestVersion: string;
  renderId: string;
  songId: string;
  fps: number;
  durationSec: number;
  totalFrames: number;
  canonicalPixelInfo: CanonicalPixelInfo;
  fixtureMappings: FixtureMapping[];
  gammaCorrection: GammaCorrectionConfig;
  brightnessLimiting: BrightnessLimitingConfig;
  frameDataPath?: string;
  framesCount: number;
}

export interface DiagnosticTest {
  id: string;
  name: string;
  description: string;
}

export interface DiagnosticTestResult {
  testId: string;
  passed: boolean;
  message?: string;
  details?: Record<string, any>;
}

export interface TestPattern {
  id: string;
  name: string;
  description: string;
  purpose: string;
}

export interface TestPatternAnalysis {
  patternId: string;
  isCorrect: boolean;
  message: string;
  details?: Record<string, any>;
}

export interface ExportReviewData {
  renderId: string;
  songId: string;
  exportManifest: ExportManifest;
  diagnosticResults: DiagnosticTestResult[];
  mappingValidation: {
    isValid: boolean;
    errors?: string[];
  };
}
