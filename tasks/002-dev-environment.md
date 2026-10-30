# Task 002 - Dev Environment

## Goal

Establish developer tooling for consistent, reproducible local development: dependency management with uv, linting and formatting with ruff, type checking with mypy, Makefile shortcuts, and pre-commit hooks.

## Inputs

`pyproject.toml` from Task 001.

## Outputs

A configured tooling setup: Makefile targets, pre-commit configuration, and tool sections in `pyproject.toml`.

## Dependencies

Task 001

## Acceptance Criteria

- `pyproject.toml` contains `[tool.ruff]` (including `[tool.ruff.format]`) and `[tool.mypy]` sections with sensible defaults
- Dependencies are managed via uv (lockfile generation documented/working)
- Makefile provides `install`, `lint`, `format`, `typecheck`, and `test` targets, where `format` runs `ruff format`
- `.pre-commit-config.yaml` wires ruff (`check` and `format`) and mypy as hooks, using the same `ruff format` command as the Makefile
- `make lint` and `make typecheck` run cleanly on the scaffold
- Unit tests pass

## Out of Scope

CI pipeline configuration and Docker packaging.

## Deliverables

Makefile
.pre-commit-config.yaml
pyproject.toml
