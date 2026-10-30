# Task 036 - Rollback Workflow

## Goal

Implement rollback of a failed apply via the Terraform MCP (destroy or targeted revert) and record the rollback. The rollback is approval-gated like any other mutating action.

## Inputs

Failed apply outcome and run state (Task 035); the Terraform MCP / Deployment Agent.

## Outputs

Rollback result recorded in the run state and audit trail.

## Dependencies

Task 035

## Acceptance Criteria

- Rolls back a failed apply via MCP destroy or targeted revert (Task 019)
- Rollback is approval-gated and requires an explicit recorded approval before it proceeds
- No direct shell execution and no AWS credentials are generated
- The terraform state file is not modified directly outside the MCP
- The rollback outcome is recorded to the audit trail (who/what/when)
- Unit tests pass

## Out of Scope

Does not generate infrastructure; does not implement state recovery (Task 037) or drift detection (Task 038).

## Deliverables

cloudpilot/graph/nodes/rollback.py
tests/test_rollback.py
