# Task 037 - State Recovery

## Goal

Implement recovery/resume of an interrupted apply using the terraform state and graph checkpoints, without corrupting the state file. This lets a run that was interrupted mid-apply continue safely.

## Inputs

Interrupted run's graph checkpoint (Task 012); terraform state as read via the Terraform MCP (Task 035 / 019).

## Outputs

A recovered run continued from a consistent point, with recovery recorded.

## Dependencies

Task 035
Task 012

## Acceptance Criteria

- Reconciles graph checkpoint with terraform state to determine a safe resume point
- Resumes the interrupted apply without corrupting or directly editing the state file
- Any terraform interaction happens only via the Terraform MCP (Task 019); no direct shell
- No AWS credentials are generated during recovery
- Recovery actions and outcome are recorded to the audit trail (who/what/when)
- Mutating recovery steps remain approval-gated
- Unit tests pass

## Out of Scope

Does not implement rollback (Task 036) or drift detection (Task 038); does not generate infrastructure.

## Deliverables

src/cloudpilot/graph/nodes/recover.py
tests/test_recover.py
