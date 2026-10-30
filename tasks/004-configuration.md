# Task 004 - Configuration

## Goal

Provide centralized application settings loaded from environment variables via pydantic-settings, exposed as a single typed config object. This gives all modules a validated, type-safe source of configuration.

## Inputs

`src/cloudpilot/core/` package from Task 001 and environment variables.

## Outputs

A typed `Settings` object, a settings accessor, and a documented `.env.example`.

## Dependencies

Task 001

## Acceptance Criteria

- `Settings` is a `pydantic-settings` `BaseSettings` subclass with typed fields
- Settings load from environment variables and an optional `.env` file
- A cached accessor (e.g. `get_settings()`) returns a singleton instance
- `.env.example` documents all settings keys with safe placeholder values
- Required-vs-optional fields and defaults are clearly defined
- No real secrets or AWS credentials are committed
- Unit tests pass

## Out of Scope

Secret management backends (e.g. AWS Secrets Manager) and runtime config reloading.

## Deliverables

src/cloudpilot/core/config.py
.env.example
tests/test_config.py
