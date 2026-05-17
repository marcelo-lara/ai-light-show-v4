# Specification: Organic Visual Math Patterns

## Objective

Document what BeatDrop or MilkDrop-style systems get right about organic visuals and translate those ideas into this project's deterministic `100x50` precompute pipeline without importing BeatDrop code or cloning the projectM evaluator surface.

## What The Research Shows

- The look is not created by one giant shader. It is staged across preset init, per-frame, and hot-path evaluation contexts.
- Organic motion usually comes from layered simple math: sine and cosine stacks, polar remaps, domain warps, decay, lag, feedback, and seeded randomness.
- Audio reaction is more stable when driven by smoothed envelopes, relative band energy, phase, and progress signals instead of raw FFT spikes alone.
- Shared state matters. MilkDrop-style systems pass derived values between stages through small shared registers and bounded local state.
- The renderer stays fast by pushing expensive work into per-frame setup and keeping per-pixel or per-point code small.

## Concepts To Borrow

### 1. Staged Evaluation

Use bounded execution stages instead of one opaque callback:

- `preset_init`: runs once when a preset or scene starts.
- `frame`: runs once per output frame.
- `cell`: optional hot-path math for per-pixel or per-sample work.
- `point`: optional hot-path math for generated traces such as waves, scans, or chase points.

This is the main structural lesson from BeatDrop and projectM expressions. Most derived values should be computed in `preset_init` or `frame`, then reused by `cell` or `point` stages.

### 2. Shared State Without Unbounded Memory

BeatDrop uses `q` and `t` variables well, but `megabuf` and `gmegabuf` are broader than we need.

For this project, prefer:

- `registers[32]`: preset-shared float registers carried from `preset_init` into each frame.
- `locals[8]`: layer or generator-local lanes carried within a single layer instance.
- explicit bounded history buffers only when a layer truly needs feedback.

Do not start with an unbounded memory API. It makes determinism, reviewability, and validation harder.

### 3. Organic Math Building Blocks

The reusable patterns are straightforward:

- oscillator stacks: mix incommensurate frequencies to avoid obvious loops.
- polar remaps: convert `(x, y)` to `(radius, angle)` before shaping motion.
- domain warps: offset coordinates with low-cost trig or noise before sampling color or intensity.
- attack or decay envelopes: smooth fast audio spikes into stable motion.
- hysteresis and lag: make motion hold and release instead of flickering.
- seeded randomness: lock variation to preset seed, scene seed, or layer seed.
- feedback fields: reuse prior-frame intent through bounded state, not unconstrained recursion.
- geometric transitions: compute wipes, radial reveals, spirals, and checker or plasma masks as scalar fields.

### 4. Performance Rules

- Per-frame work may use heavier trig, lookup generation, and cached derived constants.
- `cell` and `point` stages should stay pure, bounded, and branch-light.
- Reuse precomputed values such as angle offsets, band envelopes, POI distances, and seeded noise tables.
- Avoid unbounded loops or large memory traversal in hot paths.

## How To Apply This Here

### Execution Model

Each backend shader or layer in `backend/shaders/` should expose:

- static parameter schema
- optional `preset_init`
- optional `frame`
- one bounded renderer path: `cell` or `point`

The render engine should provide each stage with:

- time, frame index, fps, scene progress
- beat, bar, phrase, onset, and smoothed band envelopes
- normalized canvas coordinates and optional polar coordinates
- POI and fixture-relative distances where relevant
- deterministic seed inputs and shared registers

### Preset Authoring Model

Presets should declare math behavior, not custom Python orchestration.

That means the preset schema should be able to define:

- layer stack order
- modulator bindings
- stage-scoped math blocks encoded as structured AST-backed formula definitions
- shared register defaults
- bounded feedback or history requirements

We do not need projectM syntax parity. For this project we should store authored math as a small structured formula AST instead of a free-form DSL so validation, determinism, and UI inspection remain tractable.

### Recommended State Handoff

- `preset_init` writes stable register defaults and seeded offsets.
- `frame` reads analysis plus registers, writes derived motion controls, and prepares cached values for hot paths.
- `cell` or `point` only consumes those prepared values plus current coordinates or sample progress.

This is the useful part of `q` and `t` variables adapted to a cleaner API.

## Concrete Pattern Library

These should become first-class implementation targets:

1. Oscillator banks for shimmer, rotation, drift, and pulse width.
2. Polar wave and ring formulas for radial pulses, spokes, flowers, and chase fans.
3. Domain-warped gradients for fluid or watery motion.
4. Envelope plus lag operators for beat-reactive motion that does not chatter.
5. Seeded field noise for controlled variation between presets and scenes.
6. Transition masks based on direction, radius, checker, plasma, spiral, and wipe fields.

## Epic Mapping

- Epic 05 should own staged math execution, shared registers, deterministic state flow, and hot-path guardrails.
- Epic 06 should own how presets declare math blocks, state lanes, bindings, and validation.
- Epic 04, Epic 07, and Epic 08 should consume that model in concrete layer implementations under `backend/shaders/`.
- Epic 09 and Epic 10 should treat transitions as procedural scalar fields, not only opacity fades.

## Guardrails

- Do not import BeatDrop code, projectM code, or the full projectM expression API.
- Do not introduce open-ended memory features by default.
- Keep all math deterministic for the same song, preset, params, and seed.
- Keep generated outputs reviewable and cacheable in `data/artifacts/`.