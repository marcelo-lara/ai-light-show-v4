# Specification: Preset Math Schema

## Objective

Define the canonical authored file shape for presets that use staged math, shared registers, and deterministic layer composition.

## Source Location

- Preset source files live in `backend/presets/`.
- Each preset is stored as `backend/presets/{preset_id}.json`.
- These files are authored inputs, validated before render, and never written to `data/artifacts/`.

## Top-Level Shape

```json
{
  "schema_version": "1.0",
  "preset_id": "ocean_waves",
  "preset_version": 1,
  "display": {"name": "Ocean Waves", "tags": ["parcan", "ocean"]},
  "description": "Beat-reactive parcan-only ocean swell look.",
  "seed_policy": "required",
  "params": [],
  "registers": [],
  "math": {"preset_init": [], "frame": []},
  "layers": []
}
```

## Core Fields

- `schema_version`: preset schema version string.
- `preset_id`: stable unique id used in metadata and artifacts.
- `preset_version`: author-controlled breaking-change counter.
- `display`: UI-facing label and tags.
- `description`: short authored summary.
- `seed_policy`: `required` or `derived`.
- `params`: typed preset parameters.
- `registers`: preset-shared bounded state lanes, max `32`.
- `math`: preset-level staged programs.
- `layers`: ordered render stack.

## Parameters

Each entry in `params` must define:

```json
{
  "id": "speed_base",
  "type": "float",
  "default": 0.35,
  "min": 0.0,
  "max": 2.0,
  "step": 0.01,
  "group": "motion"
}
```

Supported initial types: `float`, `int`, `bool`, `color`, `enum`.

## Registers

Registers are named preset-shared lanes copied from `preset_init` into each frame.

```json
{
  "id": "phase_offset",
  "default": 0.0,
  "min": -6.28319,
  "max": 6.28319
}
```

## Layer Shape

```json
{
  "id": "wave_a",
  "shader": "wave",
  "enabled": true,
  "params": {},
  "locals": [{"id": "amp", "default": 0.0, "min": -1.0, "max": 1.0}],
  "modulators": [],
  "math": {"frame": [], "point": []}
}
```

- `shader`: registry id implemented in `backend/shaders/`.
- `locals`: layer-scoped bounded state lanes, max `8`.
- `modulators`: named bindings from Epic 05 sources into params or math refs.
- `math`: optional stage programs for this layer.

## Stage Programs

Allowed stages:

- preset-level: `preset_init`, `frame`
- layer-level: `frame`, `cell`, `point`

Each program is an ordered list of statements:

```json
{
  "assign": "reg.phase_offset",
  "expr": {"op": "rand", "args": [{"const": -3.14159}, {"const": 3.14159}]}
}
```

Assignment targets:

- `reg.{id}`
- `local.{id}`
- `out.{field}` for hot-path outputs only

## Expression Nodes

Reference nodes:

- `{"const": 0.5}`
- `{"ref": "param.speed_base"}`
- `{"ref": "mod.beat_pulse"}`
- `{"ref": "signal.beat_phase"}`
- `{"ref": "coord.x"}`
- `{"ref": "reg.phase_offset"}`
- `{"ref": "local.amp"}`

Operator nodes:

- `add`, `sub`, `mul`, `div`, `min`, `max`, `clamp`
- `sin`, `cos`, `abs`, `pow`, `sqrt`, `mix`, `smoothstep`
- `gt`, `lt`, `eq`, `and`, `or`, `select`
- `rand` only in `preset_init` or `frame`

## Validation Budgets

- no free-form DSL strings in preset files
- max `32` registers per preset
- max `8` locals per layer
- max `64` statements in preset `frame`
- max `32` statements in layer `frame`
- max `12` statements in `cell` or `point`
- hot-path stages may not call unbounded loops or access arbitrary memory

## Example

```json
{
  "schema_version": "1.0",
  "preset_id": "ocean_waves",
  "preset_version": 1,
  "display": {"name": "Ocean Waves", "tags": ["parcan", "ocean"]},
  "seed_policy": "required",
  "params": [{"id": "speed_base", "type": "float", "default": 0.35, "min": 0, "max": 2, "step": 0.01, "group": "motion"}],
  "registers": [{"id": "phase_offset", "default": 0.0, "min": -6.28319, "max": 6.28319}],
  "math": {
    "preset_init": [{"assign": "reg.phase_offset", "expr": {"op": "rand", "args": [{"const": -3.14159}, {"const": 3.14159}]}}],
    "frame": [{"assign": "reg.wave_speed", "expr": {"op": "mul", "args": [{"ref": "param.speed_base"}, {"op": "add", "args": [{"const": 1.0}, {"op": "mul", "args": [{"const": 0.35}, {"ref": "mod.beat_pulse"}]}]}]}}]
  },
  "layers": []
}
```