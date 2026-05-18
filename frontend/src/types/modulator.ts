export type ModulatorOp =
  | { op: "scale"; min: number; max: number }
  | { op: "clamp"; min: number; max: number }
  | { op: "invert" }
  | { op: "curve"; power: number }
  | { op: "smooth"; alpha: number; key?: string }
  | { op: "lag"; alpha: number; key?: string }
  | { op: "quantize"; steps: number };

export type ModulatorBinding = {
  source: string;
  lfo_freq?: number;
  lfo_shape?: "sine" | "square" | "saw";
  random_seed?: number;
  ops?: ModulatorOp[];
};

export type ModulatorValues = Record<string, number>;
