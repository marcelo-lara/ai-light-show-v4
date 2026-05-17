## LLM code size and quality rules
- Honor repository-local instruction files in `.github/instructions/`.
- Always apply `.github/instructions/.instructions.md` as the repository-wide baseline.
- For any file you read, edit, create, or review, also apply every matching domain instruction file from `.github/instructions/*.instructions.md` based on that file's path and extension.
- Current domain mappings are:
	- Container and Compose files: `.github/instructions/container-workflow.instructions.md`
	- `.devcontainer` files: `.github/instructions/devcontainer-workflow.instructions.md`
	- Frontend UI files (`*.tsx`, `*.jsx`, `*.css`, `*.scss`, `*.sass`, `*.less`, `*.html`, `*.vue`, `*.svelte`): `.github/instructions/frontend-ui.instructions.md`
	- Python and environment files (`*.py`, `*.pyi`, `*.ipynb`, `pyproject.toml`, `requirements*.txt`, `Pipfile`, `Pipfile.lock`, `poetry.lock`, `environment*.yml`, `environment*.yaml`): `.github/instructions/python-runtime.instructions.md`
- When multiple instruction files match, follow all non-conflicting directives together. If they conflict, prefer the more specific domain instruction over the general baseline.

- Prefer small files: target `<= 100` lines per file.
- If a file would exceed `100` lines, split by responsibility into focused modules.
- Keep functions small and single-purpose.
- Favor pure functions for business logic; isolate side effects at boundaries.
- Use clear names, explicit types, and consistent return shapes.
- Avoid duplicated logic; extract reusable helpers.
- Add minimal comments only when intent is not obvious from code.
- Include basic validation and error handling at I/O and integration boundaries.
- Do not keep deprecated code or compatibility shims.
- If a rule conflicts with correctness, prioritize correctness and document the tradeoff in the PR/commit message.
- Always use docker-compose for local development and testing to ensure environment consistency.


- Prefer Preact for frontend development to maintain a lightweight and efficient codebase.
- Do not run 'npm install' or 'yarn install' directly on the host machine; always use Docker to manage dependencies and ensure a consistent development environment.
- Use `docker-compose up` to start the application and `docker-compose down` to stop it, ensuring that all services are properly managed and resources are released.


## Project structure and organization rules
- Organize code by feature or domain.



## Frontend Visual and UX rules
- Prefer flexbox over grid for small/local components.
- DO NOT CREATE BORDERS unless explicitly requested.
- NEVER EVER USE ROUNDED CORNERS.
- Use CUBE CSS naming and structure; do not introduce BEM class patterns (`__`, `--`) in frontend code.
- Keep components plain: avoid wrapper-over-wrapper nesting unless required for semantics, accessibility, or behavior.
- Do not add padding or gap values unless explicitly required by the task or LoFi constraints.
- Never use mono fonts, unless strictly specified.
- Prioritize Flexbox, do not use Grid unless strictly necessary.

## graphify

For any question about this repo's architecture, structure, components, or how to add/modify/find
code, your **first tool call must be** to read `graphify-out/GRAPH_REPORT.md` (if it exists).

Triggers: "how do I…", "where is…", "what does … do", "add/modify a <component>",
"explain the architecture", or anything that depends on how files or classes relate.

After reading the report (and `graphify-out/wiki/index.md` for deep questions), answer from the
graph. Only read source files when (a) modifying/debugging specific code, (b) the graph lacks
the needed detail, or (c) the graph is missing or stale.

Type `/graphify` in Copilot Chat to build or update the graph.
