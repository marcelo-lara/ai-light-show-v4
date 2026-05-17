# Specification: Bouncing Ball Test Shader

## Objective

Define a minimal deterministic test shader named `bouncing_ball` for verifying canvas rendering, coordinate orientation, edge collisions, and frontend preview playback.

## Purpose

`bouncing_ball` is a calibration and regression shader, not a production show look.

It exists to answer three basic questions quickly:

- does the backend render the expected pixel coordinates over time
- does the cached canvas preserve motion and edge bounces correctly
- does the frontend preview display the same motion, timing, and bounds correctly

## Source Location

- Backend implementation lives in `backend/shaders/bouncing_ball.*`.
- Preset wrappers that expose it for preview testing live in `backend/presets/`.

## Visual Behavior

- Render exactly one bright point on an otherwise black canvas.
- The point starts at a deterministic authored coordinate.
- The point moves with a deterministic authored velocity.
- When the point reaches a canvas boundary, it reflects and continues, like a breakout ball.
- No trails, blur, bloom, diffusion, or secondary particles in v1.
- Default point size is one pixel.

## Default Parameters

```json
{
  "shader": "bouncing_ball",
  "params": {
    "start_x": 10,
    "start_y": 10,
    "velocity_x": 1,
    "velocity_y": 1,
    "color": "#ffffff"
  }
}
```

## Canonical Regression Preset

The first browser-regression baseline should use one fixed authored preset named `bouncing_ball_reference_v1`.

```json
{
  "schema_version": "1.0",
  "preset_id": "bouncing_ball_reference_v1",
  "preset_version": 1,
  "display": {"name": "Bouncing Ball Reference V1", "tags": ["test", "calibration", "preview"]},
  "description": "Single-point regression preset for canvas and preview validation.",
  "seed_policy": "required",
  "params": [],
  "registers": [],
  "math": {"preset_init": [], "frame": []},
  "layers": [
    {
      "id": "ball",
      "shader": "bouncing_ball",
      "enabled": true,
      "params": {
        "start_x": 97,
        "start_y": 47,
        "velocity_x": 1,
        "velocity_y": 1,
        "color": "#ffffff"
      },
      "locals": [],
      "modulators": [],
      "math": {"frame": [], "point": []}
    }
  ]
}
```

## Motion Rule

For the canonical regression preset, the motion rule must be exact:

1. Draw the point at the current integer coordinate for frame `n`.
2. Compute tentative next position from current position plus velocity.
3. If tentative `x` is outside `0..99`, invert `velocity_x` first and recompute `next_x` from the current position.
4. If tentative `y` is outside `0..49`, invert `velocity_y` first and recompute `next_y` from the current position.
5. Frame `n+1` draws at the recomputed bounded coordinate.

This rule avoids off-canvas positions and makes bounce behavior deterministic and inspectable.

## Reference Frames

The first regression baseline must use these exact coordinates for `bouncing_ball_reference_v1`.

| Frame | X | Y | Note |
|---|---:|---:|---|
| `0` | `97` | `47` | authored start |
| `1` | `98` | `48` | diagonal step |
| `2` | `99` | `49` | bottom-right corner contact |
| `3` | `98` | `48` | both axes reflected |
| `4` | `97` | `47` | reverse diagonal |
| `5` | `96` | `46` | reverse diagonal |
| `6` | `95` | `45` | reverse diagonal |
| `7` | `94` | `44` | reverse diagonal |
| `8` | `93` | `43` | default static canvas baseline frame |
| `9` | `92` | `42` | continued reverse diagonal |

## Regression Anchors

- Use frame `8` for the stable preview baseline capture.
- Use frame `2` for the edge-contact capture.
- Use frame `3` as the expected immediate post-bounce confirmation frame in metadata.

## Rules

- Motion must be deterministic for the same seed and params.
- Bounce behavior must clamp to the `100x50` canvas bounds before reflection.
- The shader must stay simple enough to reason about frame-by-frame during debugging.
- Output should make left/right and top/bottom orientation mistakes obvious.
- The shader should be preview-safe for `Play`, `Pause`, and `Stop` transport validation.

## Frontend Preview Use

- The preview console should be able to render `bouncing_ball` without requiring other production presets.
- The moving point should remain crisp when scaled in the frontend preview.
- The test is successful only if the point visibly bounces at the same edges in backend artifacts and frontend playback.

## Validation Use

Use `bouncing_ball` for:

- first-run render sanity checks
- canvas orientation checks
- playback transport checks
- shared-session preview synchronization checks
- browser visual regression baselines for motion correctness
- reference coordinate assertions against frames `0..9` of `bouncing_ball_reference_v1`