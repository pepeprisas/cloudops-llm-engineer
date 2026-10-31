# Task 033 - Audit Trail

## Goal

Implement an append-only audit log that captures every action, state transition, and approval with who/what/when. This is required by the AGENTS.md hard rules and is consumed by all mutating and approval workflows.

## Inputs

Action, state-transition, and approval events emitted across the system; configuration from Task 003; checkpoint/state references from Task 012.

## Outputs

An append-only audit log of records, each capturing actor (who), action (what), and timestamp (when).

## Dependencies

Task 003
Task 012

## Acceptance Criteria

- Records every action, state transition, and approval with who/what/when
- Log is append-only: existing records cannot be modified or deleted
- Records are typed pydantic models
- Captures every state change and approval as required by the AGENTS.md hard rules
- No AWS credentials are generated or stored in the log
- Unit tests pass

## Out of Scope

Does not make approval decisions; does not execute terraform; does not modify the terraform state file.

## Deliverables

src/cloudpilot/core/audit.py
tests/test_audit.py
