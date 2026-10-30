# Reliability and Validation Specification

## Purpose

Provide platform- and language-independent criteria for designing and evaluating
reliable software behavior, failure handling, observability, and validation.

Reliability requirements should be proportional to the impact of failure and the
operational context of the system.

## Establish Reliability Context

Before recommending or evaluating a change:

- Identify critical user and system workflows.
- Identify external dependencies and failure boundaries.
- Determine latency, availability, durability, and throughput expectations.
- Understand expected concurrency and workload scale.
- Identify existing monitoring, testing, and operational conventions.
- Determine which operations are consequential, reversible, or safe to retry.
- Identify degraded modes and recovery expectations.

State assumptions when production topology, traffic, or service-level objectives
are unknown.

## Error Semantics

Check that:

- Errors preserve enough context for diagnosis.
- Expected and exceptional outcomes are distinguishable.
- Failures are propagated, translated, or handled at appropriate boundaries.
- Exceptions or errors are not silently swallowed.
- User-facing messages do not expose secrets or internal details.
- Cleanup failures are not hidden when they affect correctness.
- Partial success is represented explicitly.

Avoid broad error handling that converts unrelated failures into misleading
fallback behavior.

## Deadlines and Cancellation

For blocking, remote, or potentially unbounded work:

- Define an appropriate deadline or timeout.
- Propagate cancellation through dependent operations.
- Release resources after cancellation.
- Distinguish caller cancellation from dependency failure.
- Ensure background work has explicit ownership and lifecycle.
- Avoid continuing consequential work after the initiating request is abandoned
  unless that behavior is intentional and observable.

Timeout values should reflect operational expectations rather than arbitrary
constants.

## Retries and Idempotency

Retries should:

- Apply only to failures likely to be transient.
- Be bounded by attempts, elapsed time, or a shared deadline.
- Use backoff and jitter where coordinated retries could amplify load.
- Respect provider guidance such as retry-after signals.
- Preserve cancellation.
- Avoid retrying invalid requests or permanent failures.
- Account for duplicate or ambiguous execution.

A consequential operation must not be retried until its idempotency and
deduplication behavior is understood.

## Concurrency and Resources

Check that:

- Shared mutable state has an explicit synchronization strategy.
- Work queues and concurrency have defined bounds.
- Backpressure prevents unbounded memory or task growth.
- Tasks, threads, processes, and connections have clear ownership.
- Files, streams, clients, locks, and other resources are reliably released.
- Shutdown waits for, cancels, or safely transfers outstanding work.
- Race conditions, deadlocks, starvation, and ordering assumptions are
  considered.

Do not add concurrency without a demonstrated benefit and a validation strategy.

## Dependency Failure and Degraded Operation

Define behavior when a dependency is slow, unavailable, or returns invalid data:

- Fail fast, retry, fall back, queue, or degrade intentionally.
- Prevent failure amplification and cascading load.
- Bound buffered work during outages.
- Consider circuit breaking or load shedding when justified.
- Make fallback data provenance and staleness visible.
- Define recovery behavior after the dependency returns.
- Avoid reporting success when required downstream work failed.

Fallback behavior must preserve security, authorization, and data-integrity
requirements.

## State and Recovery

For stateful workflows:

- Identify checkpoints and atomic boundaries.
- Define behavior after process interruption or restart.
- Prevent replay from duplicating consequential actions.
- Make transitions valid, observable, and recoverable.
- Handle partially completed work.
- Define reconciliation for inconsistent state.
- Preserve enough information to diagnose terminal failures.

## Observability

Provide signals that help answer:

- What operation failed?
- Where and why did it fail?
- Which user, request, job, or trace was affected?
- How long did it take?
- Was it retried, cancelled, degraded, or partially completed?
- Which dependency or version was involved?

Use structured logs, metrics, traces, and correlation identifiers as appropriate.
Avoid high-cardinality labels, secrets, and unnecessary sensitive content.

Important terminal states and dropped work should be observable.

## Validation Strategy

Select validation based on risk and behavior:

- Unit tests for deterministic logic and edge cases.
- Integration tests for meaningful component boundaries.
- Contract tests for external services and provider assumptions.
- End-to-end tests for critical workflows.
- Static analysis and type checking where supported.
- Load, fault-injection, or recovery tests when operational risk justifies them.

Test important failure paths, including:

- Timeout and cancellation.
- Retry exhaustion.
- Partial and ambiguous failure.
- Duplicate execution.
- Resource cleanup.
- Concurrent access.
- Dependency degradation.
- Restart and recovery.

Mocks should not hide behavior that is essential to the contract being tested.
Tests for probabilistic AI output should assert stable properties rather than
exact wording.

## Test Quality

Check that tests:

- Are deterministic and isolated.
- Verify behavior rather than implementation details where practical.
- Fail for the intended reason.
- Avoid hidden dependence on execution order, wall-clock timing, or shared state.
- Clean up resources and test data.
- Cover meaningful boundaries and failure cases.
- Do not claim production guarantees that the test environment cannot establish.

A missing test is a validation gap, not proof of a functional defect.

## Reliability Advice Output

Reliability advice should include:

1. Critical workflows and failure boundaries.
2. Error, timeout, cancellation, and retry behavior.
3. Concurrency, resource, and backpressure implications.
4. Degraded operation and recovery behavior.
5. Observability requirements.
6. Validation strategy and important failure tests.
7. Assumptions, operational risks, and unresolved decisions.

Report only sections relevant to the proposed change.
