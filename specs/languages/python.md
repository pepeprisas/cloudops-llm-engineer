# Python Engineering Specification

## Purpose

Provide Python-specific criteria for building and evaluating software changes.

Apply this specification together with the relevant workflow and domain
specifications. Follow the target project's supported Python versions, tooling,
frameworks, and conventions rather than imposing new ones.

## Establish Python Context

Inspect relevant project configuration before recommending or modifying code:

- `pyproject.toml` and other packaging metadata.
- Lockfiles and dependency-management configuration.
- Supported Python versions.
- Formatter, linter, and type-checker configuration.
- Test framework, fixtures, markers, and test layout.
- Framework-specific conventions.
- Existing public APIs and compatibility requirements.

Do not assume that a tool such as pytest, Ruff, mypy, or a specific package
manager is available unless the project demonstrates it.

## Types and Data Models

Prefer:

- Precise parameter and return annotations for maintained application code.
- Domain-specific types over unstructured dictionaries where they improve
  correctness.
- Explicit representation of optional and nullable values.
- Validated models at external, model-generated, and persistence boundaries.
- Protocols or abstract interfaces only where substitution is required.
- Consistent sync and async interfaces.

Check for:

- Mutable default arguments.
- Incorrect narrowing or unchecked `Any`.
- Type annotations that disagree with runtime behavior.
- Dataclass or model defaults shared across instances.
- Serialization behavior that omits, renames, or coerces fields unexpectedly.
- Compatibility of typing features with supported Python versions.

Typing does not replace runtime validation at untrusted boundaries.

## Errors and Control Flow

Check that:

- Exceptions are caught at boundaries that can handle them meaningfully.
- Exception types are specific enough to avoid masking unrelated failures.
- Re-raised exceptions preserve useful context and tracebacks.
- Cleanup does not suppress an active exception unintentionally.
- Expected domain outcomes are not represented by arbitrary broad exceptions.
- Public APIs document or translate important failure behavior consistently.

Avoid bare `except`, silent exception handling, and broad fallback behavior
unless the code deliberately records and safely handles every relevant failure.

## Resource Management

Use context managers or equivalent structured cleanup for resources such as:

- Files and streams.
- Network clients and responses.
- Database sessions and transactions.
- Locks and temporary resources.
- Tracing or instrumentation scopes.

Check cleanup on success, exception, timeout, and cancellation. Be cautious with
resource acquisition before entering a `try` or context-manager boundary.

## Async Code

For `asyncio` and async frameworks, check that:

- Blocking I/O and CPU-heavy work do not run on the event loop unintentionally.
- Coroutines are awaited and tasks have explicit ownership.
- Background tasks retain references and expose failures.
- Cancellation is propagated and cleanup remains cancellation-safe.
- Timeouts bound remote or potentially unbounded work.
- Concurrent work has explicit limits.
- Async clients, iterators, generators, and context managers are closed.
- Sync and async APIs are not mixed in ways that deadlock or block.
- Task groups or equivalent structured concurrency are used where appropriate.

Do not swallow cancellation through broad exception handling. A task created
with `create_task` must have a defined lifecycle and error-observation strategy.

## Concurrency and Shared State

Check that:

- Thread, process, and task safety assumptions are explicit.
- Mutable module-level or singleton state is synchronized or avoided.
- Locks protect the intended invariant and are released reliably.
- Work submitted to executors is bounded and cancellation behavior is
  understood.
- Objects crossing process boundaries are safely serializable.
- Tests do not depend on unsafe shared global state.

The presence of the GIL does not make compound operations or external resources
automatically safe.

## Dependencies and Configuration

Prefer:

- Dependencies already used by the project when they satisfy the requirement.
- Explicit version constraints consistent with project policy.
- Configuration loaded through established project mechanisms.
- Secrets supplied through protected runtime configuration.
- Lazy or controlled initialization for expensive external clients.

Check import-time side effects, optional dependency behavior, credential
rotation, and compatibility across supported Python versions.

Do not use `eval`, `exec`, unsafe YAML loaders, or pickle-like deserialization
with untrusted data.

## AI and External Provider Integration

For Python AI applications, check that:

- Sync and async SDK clients match the surrounding execution model.
- Provider clients have explicit lifecycle, timeout, and retry configuration.
- Structured model output is validated through an explicit schema.
- Provider exception classes are translated without losing important details.
- Streaming responses handle partial output, cancellation, and cleanup.
- Tool arguments are validated before invocation.
- Retries do not duplicate non-idempotent tool or persistence operations.
- Test doubles preserve important SDK and streaming behavior.

Framework convenience APIs do not replace application-level authorization,
validation, or termination controls.

## Testing

Follow existing project conventions. When pytest is used, check that:

- Fixture scope matches resource lifetime and isolation requirements.
- Mutable fixture data is not unintentionally shared.
- Async tests use the configured event-loop integration.
- Patches target the symbol used by the code under test.
- `AsyncMock` and other test doubles match real call semantics.
- Parameterization covers meaningful boundaries without obscuring failures.
- Temporary files, environment variables, and global state are restored.
- Tests avoid real model calls unless explicitly classified as integration or
  evaluation tests.

Prefer deterministic clocks, identifiers, and provider responses over patching
broad implementation details.

## Packaging and Public APIs

Check that:

- Package layout and imports work in an installed environment.
- Runtime dependencies are declared in the appropriate dependency group.
- Public exports and entry points are intentional.
- Import cycles and import-time work are avoided.
- Changes respect semantic-versioning or compatibility policy where applicable.
- Generated files and build artifacts are handled according to project policy.

Do not rely on the repository root being on `sys.path` unless the project
explicitly supports that execution model.

## Validation

Derive commands from project configuration. Relevant validation may include:

- Focused and full test suites.
- Formatting checks.
- Linting.
- Static type checking.
- Package build or installation checks.
- Framework-specific validation.
- Dependency or security analysis.

Report the exact commands and outcomes. Do not introduce or reconfigure tools
merely to claim broader validation without agreement.

## Python Advice Output

Python-specific advice should include:

1. Relevant project versions, tools, and conventions.
2. Type, API, and compatibility implications.
3. Async, concurrency, and resource-lifecycle implications.
4. Dependency and configuration implications.
5. Python-specific validation and tests.
6. Assumptions, risks, and unresolved decisions.

Report only sections relevant to the proposed change.
