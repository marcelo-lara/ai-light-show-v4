---
name: Frontend UI Conventions
description: Frontend styling and component structure defaults for UI files.
applyTo: "**/*.{tsx,jsx,css,scss,sass,less,html,vue,svelte}"
---

# Frontend UI Conventions

- Prefer Preact unless the repository already standardizes on another framework.
- Prefer flexbox for local component layout; use grid only when two-dimensional placement is required.
- Do not add borders unless explicitly requested.
- Do not use rounded corners unless explicitly requested.
- Avoid monospaced fonts unless explicitly required.
- Use CUBE CSS naming and structure; avoid BEM token patterns (__ and --).
- Keep markup shallow; avoid unnecessary wrapper elements.
- Do not add padding or gap unless the task or design spec explicitly requires it.
