# Task 042 - Automatic Retries

## Goal

Provide a reusable retry strategy for transient failures across graph nodes. Retries must be bounded, configurable, and fully logged so node authors can wrap fallible operations consistently.

## Inputs

Core configuration/settings for retry limits and backoff (Task 004).

## Outputs

A retry helper/decorator usable by graph nodes and agents.

## Dependencies

Task 004

## Acceptance Criteria

- Provides a bounded retry mechanism with a maximum attempt count and configurable backoff.
- Only transient/retryable errors are retried; non-retryable errors propagate immediately.
- Retry configuration is validated with pydantic.
- Every retry attempt, including final success or exhaustion, is logged.
- Retry logic never bypasses approval and never executes shell directly.
- Unit tests pass

## Out of Scope

Per-node retry policies, distributed/queue-based retries, and idempotency guarantees for the wrapped operations.

## Deliverables

cloudpilot/core/retry.py
tests/test_retry.py
