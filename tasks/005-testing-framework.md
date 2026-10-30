# Task 005 - Testing Framework

## Goal

Set up the pytest configuration, shared fixtures, and test layout conventions so all subsequent tasks have a consistent testing foundation.

## Inputs

`tests/` directory and `pyproject.toml` from Task 001.

## Outputs

A `conftest.py` with shared fixtures and a `[tool.pytest.ini_options]` section in `pyproject.toml`.

## Dependencies

Task 001

## Acceptance Criteria

- `pyproject.toml` contains a `[tool.pytest.ini_options]` section configuring test paths and discovery
- `tests/conftest.py` defines shared fixtures (e.g. settings override, temp dirs)
- Test naming and layout conventions are documented (in conftest or README)
- `pytest` runs and collects tests successfully from the scaffold
- Markers for unit vs integration tests are registered
- Unit tests pass

## Out of Scope

Specific feature tests (owned by their respective tasks) and CI integration.

## Deliverables

tests/conftest.py
pyproject.toml
