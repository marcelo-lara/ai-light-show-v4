export type LayerParamSchema = {
  name: string;
  type: "int" | "float" | "str" | "color" | "bool";
  default: unknown;
};

export type LayerMeta = {
  layer_id: string;
  label: string;
  param_schema: LayerParamSchema[];
};

export type LayerDef = {
  id: string;
  shader: string;
  enabled: boolean;
  params: Record<string, unknown>;
};
