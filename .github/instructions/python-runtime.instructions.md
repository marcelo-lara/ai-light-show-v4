---
name: Python Runtime Enforcement
description: Python runtime and execution rules for containerized GPU-enabled development.
applyTo: "**/{*.py,*.pyi,*.ipynb,pyproject.toml,requirements*.txt,Pipfile,Pipfile.lock,poetry.lock,environment*.yml,environment*.yaml}"
---

# Python Runtime Enforcement

- Treat the Docker image as the authoritative runtime for Python development.
- Assume the Python Docker image is NVIDIA CUDA-enabled.
- Assume local development uses an NVIDIA GeForce GTX 1650 and the container workflow is configured to use that GPU.
- For Python dependencies, execution, and tests, prefer container runtime commands over host-machine Python commands unless explicitly requested otherwise.
- Always prefer running tests inside the Docker environment.
- On the host, check for an existing Python virtual environment before creating a new one.
