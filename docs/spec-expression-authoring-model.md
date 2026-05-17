# Specification: Expression Authoring Model

## Decision

Use a structured formula AST embedded in preset JSON. Do not use a free-form string DSL for authored preset math.

## Why

- Validation is easier before render time.
- Deterministic budgets are enforceable per stage.
- Frontend tooling can inspect references, operators, and targets without reparsing code.
- Safer scoping makes it harder to recreate projectM-style open-ended runtime behavior by accident.
- A JSON AST fits the existing preset-schema direction better than a second parser language.

## Rejected Option: Free-Form DSL

We are not choosing a projectM-like script surface because it would:

- require a parser, error recovery, and tooling surface we do not need yet
- blur the boundary between author-time expressions and engine implementation logic
- make hot-path budget enforcement harder
- invite pressure toward unsupported features such as arbitrary memory access and loop-heavy code

## Required AST Features

- stage-scoped programs for `preset_init`, `frame`, `cell`, and `point`
- explicit assignment targets
- typed references to params, signals, modulators, coords, registers, locals, and outputs
- a small operator set for arithmetic, shaping, comparison, selection, and trig
- static stage validation before render starts

## Hot-Path Rules

- `cell` and `point` programs stay expression-oriented and bounded.
- No loops in authored AST v1.
- No arbitrary memory access in authored AST v1.
- Random sources are allowed only in `preset_init` or `frame`.
- Expensive derived values should be prepared in `frame` and consumed by reference in hot paths.

## Engine Consequences

- Epic 05 owns execution order, scoping, and budgets.
- Epic 06 owns the serialized AST format and validation errors.
- Backend shaders remain the execution host for outputs and domain-specific fields.
- Frontend inspectors can show refs, targets, and operator trees directly from JSON metadata.

## Authoring Consequences

- Preset authors write formulas as structured data, not ad hoc script text.
- Shared state remains explicit through named registers and locals.
- Migration to richer tooling later can still generate this AST from a visual editor or a compact shorthand, but the stored artifact remains structured JSON.

## Escape Hatch

If authoring ergonomics later become a real blocker, we may add an author-side shorthand that compiles into this AST. The source of truth should still remain the validated AST in preset files.