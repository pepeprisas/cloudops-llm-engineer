# Task 028 - Documentation Agent

## Goal

Implement a single-responsibility Documentation Agent that produces a human-readable summary of the deployment plan and the planned changes. The summary supports the human approver during review.

## Inputs

Generated Terraform plan/configuration produced by Task 020.

## Outputs

Human-readable summary (pydantic model and/or markdown) of the deployment plan and planned changes.

## Dependencies

Task 020

## Acceptance Criteria

- Summarizes the resources to be created, changed, and destroyed
- Output is human-readable and suitable for an approver to review
- Summary is returned through a typed pydantic model
- Every summary action is logged per docs/security.md
- Unit tests pass

## Out of Scope

Does not modify the Terraform; does not execute terraform; does not make approval decisions.

## Deliverables

cloudpilot/agents/documentation.py
tests/test_documentation_agent.py
