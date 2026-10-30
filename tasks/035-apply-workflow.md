# Task 035 - Apply Workflow

## Goal

Implement the DEPLOYING graph node that invokes terraform apply via the Deployment Agent / Terraform MCP only after approval, and records the outcome. This is the node that drives a real infrastructure change.

## Inputs

Approved graph state (Task 029); the Deployment Agent and Terraform MCP (Task 034).

## Outputs

Apply result recorded in the run state and audit trail.

## Dependencies

Task 034
Task 029

## Acceptance Criteria

- DEPLOYING node invokes apply only via the Deployment Agent / Terraform MCP (Task 019)
- Apply requires an explicit recorded approval before it proceeds
- No direct shell execution and no AWS credentials are generated
- The terraform state file is not modified directly by this node
- The apply outcome (success/failure) is recorded to the audit trail (who/what/when)
- Unit tests pass

## Out of Scope

Does not generate infrastructure; does not implement rollback (Task 036), state recovery (Task 037), or the approval gate itself (Task 029).

## Deliverables

cloudpilot/graph/nodes/apply.py
tests/test_apply.py
