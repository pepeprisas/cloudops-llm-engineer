# Task 029 - Approval Workflow

## Goal

Interrupt the LangGraph state machine at WAITING_FOR_APPROVAL using the checkpointer and expose an approve action that resumes the run. No mutating operation may proceed without an explicit approval.

## Inputs

Graph state at the WAITING_FOR_APPROVAL node; checkpointer from Task 010; review findings from upstream agents.

## Outputs

A paused checkpoint at WAITING_FOR_APPROVAL and an approve action that records the approval and resumes the run.

## Dependencies

Task 010
Task 011

## Acceptance Criteria

- Graph interrupts at WAITING_FOR_APPROVAL and persists state via the checkpointer
- An approve action resumes the run from the checkpoint
- No mutating action (apply/destroy/rollback) proceeds without approval
- Approval requires explicit human action and is recorded to the audit trail (who/what/when)
- No direct shell execution; any terraform work happens via the Terraform MCP (Task 019)
- Unit tests pass

## Out of Scope

Does not implement the reject, resume-from-disk, or cancel paths (Tasks 030, 031, 032); does not perform the apply itself (Task 035).

## Deliverables

cloudpilot/graph/nodes/approval.py
tests/test_approval.py
