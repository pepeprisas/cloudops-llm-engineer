# Task 032 - Cancel Workflow

## Goal

Implement the ability to cancel an in-flight deployment safely at any pausable point. Cancellation stops further progress without leaving infrastructure or state in an inconsistent condition.

## Inputs

Active or paused graph run; human-supplied cancel signal.

## Outputs

A cancelled run in a terminal state, with the cancellation recorded.

## Dependencies

Task 029

## Acceptance Criteria

- Cancel transitions the run to a terminal cancelled state at a safe, pausable point
- No partial mutating action is started or left running as a result of cancel
- The cancellation is recorded to the audit trail (who/what/when)
- No direct shell execution; nothing bypasses the Terraform MCP (Task 019)
- Cancel does not require or bypass approval to stop a run
- Unit tests pass

## Out of Scope

Does not implement rollback of already-applied resources (Task 036) or state recovery (Task 037); does not implement approval, reject, or resume (Tasks 029, 030, 031).

## Deliverables

cloudpilot/graph/cancel.py
tests/test_cancel.py
