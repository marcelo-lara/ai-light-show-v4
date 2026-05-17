## Epic 13: Ocean Waves Shader

Implementation note: use `docs/spec-ocean-waves-shader.md` for the visual target and parameter intent.

### Backend Track

- [ ] 13.B1 Ocean waves layer spec: define a parcan-oriented shader named `ocean_waves` in `backend/shaders/`.
- [ ] 13.B2 Left-to-right swell motion: make the dominant wave bodies travel from left to right across the canvas.
- [ ] 13.B3 Three-field composition: use exactly three layered fields in v1 for primary swell mass, depth contrast, and restrained crest emphasis.
- [ ] 13.B4 Ocean palette defaults: define deep-blue base, darker troughs, and restrained cyan-highlight behavior.
- [ ] 13.B5 Contrast shaping: prefer smoothed contrast functions such as `mix`, `smoothstep`, and `clamp` over noisy or hard-thresholded crest logic.
- [ ] 13.B6 Parcan sampling intent: shape the look so broad swells remain readable when sampled by fixed parcan anchor coordinates.
- [ ] 13.B7 Parameter schema: define controls for `base_color`, `highlight_color`, `wave_speed`, `wave_scale`, `contrast_depth`, `foam_intensity`, and `parcan_only`.
- [ ] 13.B8 Preset integration: make the shader usable from the preset and layer system, including the `ocean_waves` preset.

### Frontend Track

- [ ] 13.F1 Shader metadata types: add frontend-readable types for the `ocean_waves` shader and its parameter schema.
- [ ] 13.F2 Parcan preview readiness: make the UI able to preview ocean-wave output as a parcan-first look.
- [ ] 13.F3 Contrast review readiness: ensure the preview preserves large swell readability and inner-contrast structure.

### Validation Track

- [ ] 13.V1 Direction test: prove the dominant motion reads left to right.
- [ ] 13.V2 Swell scale test: prove the output contains large wave bodies rather than high-frequency ripples.
- [ ] 13.V3 Contrast structure test: prove each swell contains readable interior contrast rather than a flat body fill.
- [ ] 13.V4 Parcan readability test: prove parcan-sampled output preserves the ocean-wave motion and internal contrast.
- [ ] 13.V5 Exact preset payload test: prove the canonical `ocean_waves` preset loads with the documented payload and defaults.
- [ ] 13.V6 Browser regression test: add browser-visible regression coverage for baseline swell readability, left-to-right movement, and inner contrast.