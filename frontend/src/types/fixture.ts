export type FixtureLocation = { x: number; y: number; z: number };

export type FixtureInstance = {
  id: string;
  name: string;
  fixture: string;
  base_channel: number;
  location: FixtureLocation;
};

export type PoiCalibration = { pan: number; tilt: number };

export type PointOfInterest = {
  id: string;
  name: string;
  location: FixtureLocation;
  fixtures: Record<string, PoiCalibration>;
};

export type FixtureSample = {
  fixture_id: string;
  r: number;
  g: number;
  b: number;
  px: number;
  py: number;
};

export type MappingConfig = {
  pixel_order: "linear" | "serpentine";
  gamma: number;
  brightness_limit: number;
  canvas_width: number;
  canvas_height: number;
};
