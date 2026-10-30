# Task 030 - Reject Workflow

## Goal

Implement the reject path from WAITING_FOR_APPROVAL. When a human rejects the plan, the run records the reason and terminates cleanly without applying any infrastructure.

## Inputs

Paused graph state at WAITING_FOR_APPROVAL (Task 029); human-supplied rejection reason.

## Outputs

A terminated run state with the rejection reason recorded.

## Dependencies

Task 029

## Acceptance Criteria

- Reject action transitions the run out of WAITING_FOR_APPROVAL to a terminal state
- The rejection reason is captured and recorded to the audit trail (who/what/when)
- No apply/destroy/rollback or other mutating action runs on rejection
- No direct shell execution; nothing bypasses the Terraform MCP (Task 019)
- Run terminates cleanly without leaving the graph in a stuck state
- Unit tests pass

## Out of Scope

Does not implement approval, resume, or cancel (Tasks 029, 031, 032); does not perform any infrastructure changes.

## Deliverables

cloudpilot/graph/nodes/reject.py
tests/test_reject.py
