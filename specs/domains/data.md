# Data and Persistence Specification

## Purpose

Provide platform- and language-independent criteria for designing and evaluating
data access, persistence, retrieval, caching, and state management.

Apply only the sections relevant to the system under consideration. Do not
assume a database, cache, queue, or vector store exists without evidence.

## Establish Data Context

Before recommending or evaluating a change:

- Identify authoritative and derived data stores.
- Trace data from input through storage, retrieval, and deletion.
- Identify users, tenants, sessions, or other isolation boundaries.
- Determine ownership of each data set.
- Identify consistency, durability, latency, and availability requirements.
- Review existing schemas, migrations, query patterns, and access layers.
- Identify sensitive, regulated, or externally sourced data.

State assumptions when runtime configuration or operational scale is unknown.

## Data Models and Integrity

Check that:

- Types and constraints represent domain invariants.
- Required, optional, and default values are intentional.
- Unique, foreign-key, and check constraints match application behavior.
- Relationships cannot create unintended orphaned or duplicate records.
- Time, ordering, identifiers, and numeric precision are represented correctly.
- Application validation and storage constraints provide compatible guarantees.
- Schema evolution accounts for existing data.

Do not rely solely on model-generated output or application prompts to preserve
data integrity.

## Queries and Access

Check that:

- Untrusted values are parameterized or handled through safe APIs.
- Queries enforce user, tenant, and resource authorization.
- Reads request only the data they require.
- Pagination or bounds exist for potentially large result sets.
- Query patterns can use appropriate indexes.
- Repeated access does not create avoidable N+1 behavior.
- Query results handle missing, null, stale, or duplicated data correctly.

Performance claims should be supported by expected scale, query plans, metrics,
or reproducible measurements where available.

## Transactions and Concurrency

Define:

- Which operations must succeed or fail together.
- Appropriate transaction boundaries.
- Isolation and locking requirements.
- Behavior for concurrent updates.
- Conflict detection or optimistic concurrency strategy.
- Lock ordering and deadlock handling.
- Cleanup behavior after cancellation or failure.

Avoid transactions that are too broad for operational safety or too narrow to
preserve required invariants.

## Retries, Events, and Duplicate Work

For operations that may be retried, replayed, or delivered more than once:

- Define idempotency behavior.
- Use stable operation or deduplication identifiers where appropriate.
- Prevent duplicate records and repeated consequential side effects.
- Define ordering requirements and tolerance for out-of-order delivery.
- Handle partial failure between storage and message publication.
- Consider an outbox, inbox, or equivalent coordination pattern when justified.

Do not claim exactly-once behavior unless every relevant boundary supports it.

## Caches, Memory, and Retrieval

Check that:

- Cache keys include every required isolation dimension.
- Expiration and invalidation behavior are defined.
- Stale data is acceptable or detected.
- Cache failure does not silently violate correctness or authorization.
- Stored conversation or agent state has explicit ownership and lifecycle.
- Retrieval filters enforce authorization before results reach a model.
- Vector similarity is not treated as proof of identity, authorization, or
  factual correctness.
- Retrieved content retains useful provenance and freshness information.

## Migrations and Compatibility

Migrations should consider:

- Compatibility with old and new application versions.
- Deployment and rollback ordering.
- Lock duration and impact on live traffic.
- Backfills that operate in bounded batches.
- Index construction and resource use.
- Defaults and nullability for existing rows.
- Recovery after partial completion.
- Validation that migrated data satisfies new invariants.

Destructive changes require explicit approval and a verified recovery strategy.

## Privacy and Lifecycle

Define:

- The purpose and lawful basis for collecting sensitive data where applicable.
- Data minimization requirements.
- Retention, deletion, export, and correction behavior.
- Encryption and key-management requirements.
- Redaction of logs, traces, prompts, and model-provider requests.
- Access auditing and tenant isolation.
- Treatment of backups, derived data, embeddings, and cached copies.

Deletion requirements should account for secondary stores and derived
representations, not only the primary record.

## Connections and Failure Handling

Consider:

- Connection and client lifecycle.
- Pool sizing and resource limits.
- Timeouts and cancellation propagation.
- Credential rotation.
- Health checks and reconnection.
- Partial writes and ambiguous outcomes.
- Provider or storage unavailability.
- Backpressure during degraded operation.

Resources must be released reliably on success, failure, and cancellation.

## Validation and Testing

Test important behavior such as:

- Constraints and invalid input.
- Transaction rollback and partial failure.
- Concurrent modification.
- Retry and duplicate delivery.
- Tenant and user isolation.
- Cache invalidation and stale reads.
- Migration compatibility and recovery.
- Retention and deletion across relevant stores.

Use production-like storage or contract tests when mocks would hide meaningful
database or provider behavior.

## Data Advice Output

Data advice should include:

1. Affected data and ownership boundaries.
2. Schema, query, transaction, and concurrency implications.
3. Retry, replay, cache, and consistency behavior.
4. Migration and compatibility requirements.
5. Privacy, retention, and isolation requirements.
6. Validation strategy.
7. Assumptions, operational risks, and unresolved decisions.

Report only sections relevant to the proposed change.
