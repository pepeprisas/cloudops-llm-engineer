# Task 012 - Checkpoint Storage

## Goal

Provide a concrete checkpointer backend using SQLite for local development, behind the pluggable persistence interface so other backends can be swapped in.

## Inputs

The checkpointer interface from Task 011 and `Settings` (database path/URL) from Task 004.

## Outputs

A SQLite-backed checkpointer implementation and a factory selecting it via config.

## Dependencies

Task 011

## Acceptance Criteria

- Implements a SQLite-backed checkpointer satisfying the Task 011 interface
- Backend selection is driven by `Settings` (e.g. checkpoint URL/path)
- Checkpoints persist across process restarts and can be resumed
- Schema/connection setup is created idempotently on first use
- Stored data contains no AWS credentials or secrets
- Unit tests pass (write, restart-simulation, resume round-trip)

## Out of Scope

Non-SQLite production backends (e.g. Postgres) and migration tooling.

## Deliverables

src/cloudpilot/graph/checkpoints.py
tests/test_checkpoints.py
