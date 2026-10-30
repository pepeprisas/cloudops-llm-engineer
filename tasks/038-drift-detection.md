# Task 038 - Drift Detection

## Goal

Implement detection of drift between deployed infrastructure and the desired state by running terraform plan via the Terraform MCP. It reports differences so they can be surfaced for review.

## Inputs

Desired-state Terraform configuration and deployed infrastructure, accessed via the Terraform MCP (Task 019).

## Outputs

Structured drift report (pydantic model) describing detected differences.

## Dependencies

Task 019

## Acceptance Criteria

- Detects drift by running terraform plan via the Terraform MCP (Task 019)
- Reports added, changed, and removed resources relative to desired state
- No direct shell execution and no AWS credentials are generated
- The terraform state file is not modified by drift detection
- Drift detection runs are recorded to the audit trail (who/what/when)
- Unit tests pass

## Out of Scope

Does not remediate drift, apply changes, or roll back (Tasks 035, 036); read-only plan against the desired state.

## Deliverables

cloudpilot/graph/nodes/drift.py
tests/test_drift.py
