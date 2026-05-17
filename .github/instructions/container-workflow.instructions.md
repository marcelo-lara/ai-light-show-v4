---
name: Container Workflow Defaults
description: Docker and compose workflow defaults for container configuration and dev environment tasks.
applyTo: "**/{Dockerfile,Dockerfile.*,docker-compose*.yml,docker-compose*.yaml,compose*.yml,compose*.yaml}"
---

# Container Workflow Defaults

- When a repository has a Docker Compose workflow, prefer compose-based local development commands.
- For JavaScript dependencies in compose-based projects, run install commands in containers/services, not directly on the host.
- Prefer docker compose up to start services and docker compose down to stop them.
- For Python development, assume the Docker image is NVIDIA CUDA-enabled.
- Assume local development uses an NVIDIA GeForce GTX 1650 and that the container workflow is configured to use that GPU.
- Treat the Docker image as the authoritative developer runtime for Python: dependency installation, execution, and testing should target the container runtime.
- Always prefer running tests inside the Docker environment.
- If a repository does not use Docker Compose, do not force a container workflow.
