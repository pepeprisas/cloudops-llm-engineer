# Software Architecture Specification

## Purpose

Provide platform- and language-independent criteria for designing and evaluating
changes to software architecture.

Apply these criteria in proportion to the size and risk of the change. Do not
introduce architectural complexity when a local implementation is sufficient.

## Establish Architectural Context

Before recommending or evaluating a design:

- Read available architecture and project documentation.
- Identify the affected components and their responsibilities.
- Trace relevant dependencies and dependency direction.
- Identify public and internal interfaces.
- Determine data ownership and persistence boundaries.
- Understand deployment, runtime, and communication patterns where relevant.
- Compare with established patterns in the repository.

When documentation is absent or incomplete, infer cautiously from code and label
those conclusions as assumptions.

## Responsibilities and Boundaries

Check that:

- New behavior belongs in the selected component.
- Components have clear, cohesive responsibilities.
- Business logic is not misplaced in transport, persistence, or presentation
  layers.
- Shared code is genuinely reusable rather than misplaced domain logic.
- The design does not create unnecessary coupling or circular dependencies.
- Boundaries can be understood and tested independently.

Do not prescribe services, layers, interfaces, or abstractions without a
demonstrated need.

## Dependency Design

Check that:

- Dependencies flow in the intended direction.
- High-level policy is not unnecessarily coupled to infrastructure details.
- External services and providers are isolated behind suitable boundaries when
  substitution, testing, or failure handling requires it.
- New dependencies provide sufficient value for their operational and
  maintenance cost.
- Dependency versions and compatibility constraints are understood.

## Interfaces and Contracts

For APIs, events, tools, schemas, and internal interfaces, consider:

- Ownership and intended consumers.
- Input, output, and error semantics.
- Validation and authorization boundaries.
- Backward and forward compatibility.
- Versioning and deprecation requirements.
- Idempotency and retry behavior.
- Whether the contract exposes implementation details unnecessarily.

Contract changes should identify affected producers, consumers, and rollout
requirements.

## Data Ownership and State

Check that:

- Each stateful component has clear ownership of its data.
- Components do not bypass established data-access boundaries.
- Transactions match consistency requirements.
- Cache, replicated, and derived state have defined consistency behavior.
- Migrations preserve compatibility during deployment and rollback.
- Lifecycle, retention, privacy, and deletion requirements are considered.

## Failure and Operational Design

Consider:

- Partial failures and unavailable dependencies.
- Timeouts, cancellation, retries, and backpressure.
- Resource ownership and cleanup.
- Startup, shutdown, recovery, and rollback behavior.
- Observability at important boundaries.
- Deployment ordering and configuration changes.
- Whether feature flags or staged rollout are warranted.

The design should make important failure behavior explicit rather than relying on
implicit provider or framework defaults.

## Simplicity and Evolution

Prefer designs that:

- Solve the current requirement with the fewest necessary concepts.
- Match established project patterns unless deviation has a clear benefit.
- Keep likely changes localized.
- Avoid premature generalization.
- Make irreversible decisions explicit.
- Leave extension points only where credible variation exists.

Document intentional technical debt and the conditions under which it should be
revisited.

## Architecture Advice Output

Architecture advice should include:

1. Relevant existing components and constraints.
2. Proposed responsibility and boundary changes.
3. Affected dependencies, interfaces, and data ownership.
4. Failure, deployment, and compatibility implications.
5. Alternatives considered and why they were rejected.
6. Assumptions, risks, and unresolved decisions.

For small changes, report only applicable sections. Do not inflate a local
change into a system-wide redesign.
