# Specification: Ocean Waves Shader

## Objective

Define a parcan-oriented shader named `ocean_waves` that mimics slow, deep-blue ocean wave motion moving from left to right with large swells and inner contrast.

## Visual Reference Intent

Use the provided ocean-water reference as style guidance only.

Target qualities:

- deep blue base tone
- large slow-moving horizontal wave bodies
- visible inner contrast inside each swell, not flat color bands
- cinematic motion that drifts left to right rather than flickering or strobing

Do not copy source media frames. Recreate the feel through deterministic shader math.

## Source Location

- Backend implementation lives in `backend/shaders/ocean_waves.*`.
- Presets that expose the look live in `backend/presets/`.

## Fixture Intent

- This look is primarily for parcan fixtures.
- Output should read as broad wash motion sampled by parcans from stable canvas positions.
- Moving heads are not the primary target for v1 of this shader.

## Motion Model

- Wave energy travels from left to right across the canvas.
- The dominant structures are large swells, not fine ripples.
- At least two overlapping wave fields should create internal light or dark contrast within the body of the wave.
- Motion should remain smooth and slow enough to feel like ocean mass rather than a scanner effect.

## Math Brief

Use exactly three layered fields in v1:

1. Primary swell field
	A low-frequency horizontal carrier that defines the big body of each wave and the dominant left-to-right drift.
2. Depth field
	A second broad field with a different phase and slightly different scale that darkens or lifts interior regions inside the swell.
3. Crest contrast field
	A restrained highlight field that shapes inner contrast and subtle crest emphasis without turning into foam noise.

Preferred shaping functions:

- prefer `sin` or `cos` for the broad carrier fields
- prefer `mix`, `smoothstep`, and `clamp` to shape contrast transitions
- prefer `min` or `max` only after smoothing when combining crest or trough emphasis
- use `abs` sparingly and only when followed by smoothing, to avoid harsh mirrored seams

Avoid for v1:

- high-frequency noise as a primary texture source
- hard binary thresholding for crest edges
- small repeated ripples that become aliasing on the `100x50` canvas

## Field Composition Targets

- Primary swell field width should read as roughly `12` to `24` canvas columns per swell.
- Depth field should be slower than the primary carrier and offset enough to create visible internal dark or bright pockets.
- Crest contrast field should occupy only a minority of the swell body and must not replace the body itself.
- The final image should still read as one coherent ocean mass, not three visibly separate bands.

## Color Model

- Default palette centers on deep blue, blue-cyan highlights, and darker navy troughs.
- Inner contrast should come from layered luminance variation and subtle hue separation, not only brightness scaling.
- Highlights should appear inside and along the face of a swell, not only on the leading edge.

## Parameters

- `base_color`: default deep blue.
- `highlight_color`: default blue-cyan.
- `wave_speed`: left-to-right drift speed.
- `wave_scale`: size of the primary swell bodies.
- `contrast_depth`: strength of internal light or dark variation.
- `foam_intensity`: optional subtle crest emphasis, kept restrained in v1.
- `parcan_only`: boolean default `true` for the first preset using this shader.

## Parcan Sampling Read

- Parcans should sample stable anchor positions spread across the canvas width.
- Sampling should preserve the broad body of a swell rather than a single noisy pixel.
- Adjacent parcan anchors should read as phase-shifted parts of the same moving wave, not independent flicker.
- Leftmost parcans should enter the bright face of a swell before rightmost parcans when the wave travels left to right.
- For review and validation, treat parcan sampling as an area read over a small local window rather than a one-pixel probe.

Recommended v1 sampling window:

- weighted local average over a `5x5` canvas neighborhood centered on the parcan anchor coordinate

## Canonical Preset Payload

The first production preset should use the same id as the shader goal: `ocean_waves`.

```json
{
	"schema_version": "1.0",
	"preset_id": "ocean_waves",
	"preset_version": 1,
	"display": {"name": "Ocean Waves", "tags": ["parcan", "ocean", "wash"]},
	"description": "Parcan-first deep-blue ocean swell look with left-to-right motion and inner contrast.",
	"seed_policy": "required",
	"params": [
		{"id": "base_color", "type": "color", "default": "#0b3f88", "group": "palette"},
		{"id": "highlight_color", "type": "color", "default": "#6fd3ff", "group": "palette"},
		{"id": "wave_speed", "type": "float", "default": 0.18, "min": 0.10, "max": 0.30, "step": 0.01, "group": "motion"},
		{"id": "wave_scale", "type": "float", "default": 0.78, "min": 0.55, "max": 1.10, "step": 0.01, "group": "motion"},
		{"id": "contrast_depth", "type": "float", "default": 0.58, "min": 0.35, "max": 0.85, "step": 0.01, "group": "contrast"},
		{"id": "foam_intensity", "type": "float", "default": 0.10, "min": 0.00, "max": 0.25, "step": 0.01, "group": "contrast"},
		{"id": "parcan_only", "type": "bool", "default": true, "group": "fixture"}
	],
	"registers": [],
	"math": {"preset_init": [], "frame": []},
	"layers": [
		{
			"id": "ocean_wash",
			"shader": "ocean_waves",
			"enabled": true,
			"params": {
				"base_color": "#0b3f88",
				"highlight_color": "#6fd3ff",
				"wave_speed": 0.18,
				"wave_scale": 0.78,
				"contrast_depth": 0.58,
				"foam_intensity": 0.10,
				"parcan_only": true
			},
			"locals": [],
			"modulators": [],
			"math": {"frame": [], "point": []}
		}
	]
}
```

## Required Dynamic Behavior

Even if the first stored payload remains static, validation should require these effective runtime behaviors:

- beat pulse increases effective `wave_speed` within the declared preset bounds
- high-band energy or FFT motion increases effective `contrast_depth` within the declared preset bounds
- low-band energy may deepen body weight, but must not overpower directional readability

## Guardrails

- Avoid tiny noisy detail that will collapse on the `100x50` canvas.
- Avoid sharp sawtooth edges; motion should stay soft and volumetric.
- Avoid rainbow palettes in v1; the look should stay recognizably oceanic.
- Avoid relying on moving-head-only semantics for the first implementation.

## Validation Use

Use `ocean_waves` to verify:

- left-to-right directional motion is readable in the preview
- parcan-sampled output preserves large wave bodies
- inner contrast survives low-resolution rendering
- the frontend preview displays broad oceanic motion without banding or orientation errors

## Expected Tests

- direction test: the dominant crest centroid shifts rightward between two fixed playback anchors
- scale test: swell bodies remain broad enough to read on the `100x50` canvas and do not collapse into fine ripples
- contrast test: each sampled swell region contains at least one readable interior luminance change rather than a flat fill
- parcan sampling test: left, center, and right parcan anchors observe the same traveling wave with time-delayed phase, not unrelated flicker
- browser preview test: the frontend preview preserves broad wave mass, inner contrast, and left-to-right movement for the `ocean_waves` preset