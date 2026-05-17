## Epic 12: Render Diagnostics

Validation note: use `docs/spec-browser-visual-regression.md` as the browser-driven source of truth for visual regression coverage, baseline capture rules, and failure artifacts.

### Backend Track

- [ ] 12.B1 Diagnostics summary: compute brightness, average color, frame delta, blank-frame warnings, and render duration.
- [ ] 12.B2 Variety metrics: add beat-response and section-variation style signals that flag static or repetitive renders.
- [ ] 12.B3 Contact sheets: generate contact sheets for each render.
- [ ] 12.B4 Preview strip or GIF: generate a short preview strip or GIF for each render.

### Frontend Track

- [ ] 12.F1 Diagnostics types: add frontend types for diagnostics summaries and warnings.
- [ ] 12.F2 Diagnostics view: surface diagnostics summaries and warnings in the console UI.
- [ ] 12.F3 Diagnostics asset view: surface contact sheets and preview assets in the UI.

### Validation Track

- [ ] 12.V1 Blank render test: catch obviously blank renders.
- [ ] 12.V2 Static render test: catch accidentally static renders.
- [ ] 12.V3 Regression change test: catch accidental visual output changes.
- [ ] 12.V4 Browser baseline suite: capture the named browser cases from `spec-browser-visual-regression.md` against the live Dockerized app.
- [ ] 12.V5 Overlay regression suite: compare fixture and POI overlay baselines separately from raw canvas baselines.
- [ ] 12.V6 Diagnostics asset regression suite: compare contact sheets, preview strips, and warning states in the browser UI.
- [ ] 12.V7 Review-console regression suite: compare approval, fullscreen, frame-inspector, timeline, and A/B compare states in the browser UI.
