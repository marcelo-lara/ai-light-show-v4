---
name: Devcontainer Workflow Defaults
description: Container workflow defaults for repositories using a .devcontainer setup.
applyTo: "**/.devcontainer/**"
---

# Devcontainer Workflow Defaults

- Prefer container-first development commands for repositories configured with devcontainers.
- Keep dependency installs and tooling execution inside the containerized environment where possible.
- Avoid host-only install guidance when the repository standard is devcontainer-based development.
