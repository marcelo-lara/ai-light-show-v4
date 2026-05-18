export type PresetParamDef = {
  id: string;
  type: "float" | "int" | "bool" | "color" | "enum";
  default: unknown;
  min?: number;
  max?: number;
  step?: number;
  group?: string;
};

export type PresetDisplay = {
  name: string;
  tags: string[];
};

export type PresetSummary = {
  preset_id: string;
  preset_version: number;
  display: PresetDisplay;
  description: string;
  seed_policy: "required" | "derived";
  params: PresetParamDef[];
};
