# Task 001 - Project Scaffold

## Goal

Create the repository skeleton for CloudPilot, including Python packaging and the top-level package directories. This establishes the import structure that all subsequent tasks build on.

## Inputs

None

## Outputs

Python package layout under `src/cloudpilot/` with subpackages (`agents`, `graph`, `mcp`, `api`, `models`, `core`), a `tests/` directory, and project packaging metadata.

## Dependencies

None

## Acceptance Criteria

- `pyproject.toml` declares the project, Python version, and build backend
- `src/cloudpilot/` and subpackages (`agents`, `graph`, `mcp`, `api`, `models`, `core`) each contain `__init__.py` and are importable
- `tests/` exists and is collectable by pytest (test layout is delivered by Task 005)
- `pip install -e .` (or `uv pip install -e .`) succeeds
- README.md describes project purpose and basic layout, including the import-direction contract
- Runtime dependencies are declared but not pinned; no lockfile is committed

## Out of Scope

Dev tooling configuration, dependency pinning, and any business logic in the packages.

## Deliverables

pyproject.toml
src/cloudpilot/__init__.py
src/cloudpilot/agents/__init__.py
src/cloudpilot/graph/__init__.py
src/cloudpilot/mcp/__init__.py
src/cloudpilot/api/__init__.py
src/cloudpilot/models/__init__.py
src/cloudpilot/core/__init__.py
README.md
.gitignore
