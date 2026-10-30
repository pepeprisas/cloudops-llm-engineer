# Task 003 - Logging

## Goal

Provide centralized, structured application logging (JSON-capable) that every module uses. This ensures every action is consistently logged, supporting the security requirement that all actions be auditable.

## Inputs

`cloudpilot/core/` package from Task 001.

## Outputs

A logging module exposing a configured logger factory and setup function used across the codebase.

## Dependencies

Task 001

## Acceptance Criteria

- `get_logger(name)` returns a configured logger
- A setup function configures handlers and supports JSON-formatted output (toggleable for local human-readable mode)
- Log records include timestamp, level, logger name, and message at minimum
- No secrets or AWS credentials are ever logged
- Every action is loggable in a structured, audit-friendly format (per docs/security.md)
- Unit tests pass

## Out of Scope

Log shipping/aggregation backends and per-module log call instrumentation.

## Deliverables

cloudpilot/core/logging.py
tests/test_logging.py
