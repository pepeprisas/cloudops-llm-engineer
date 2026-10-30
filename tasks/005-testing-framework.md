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
- `tests/conftest.py` documents the test naming, marker, and layout conventions
- Shared fixtures are added by the task that needs them; `conftest.py` defines none in advance, because no fixture has a demonstrable consumer yet (Task 004 supplies `Settings`)
- `pytest` runs and collects tests successfully from the scaffold
- Markers for unit vs integration tests are registered
- Unit tests pass

## Out of Scope

Specific feature tests (owned by their respective tasks) and CI integration.

## Deliverables

tests/conftest.py
pyproject.toml
