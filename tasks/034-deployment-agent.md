# Task 034 - Deployment Agent

## Goal

Implement the Deployment Agent that orchestrates the DEPLOYING phase by executing terraform apply via the Terraform MCP, behind approval. It only orchestrates apply/destroy operations and never generates infrastructure itself.

## Inputs

Approved deployment plan and graph state; the Terraform MCP from Task 019.

## Outputs

Orchestrated apply/destroy invocation results and recorded outcome.

## Dependencies

Task 019

## Acceptance Criteria

- Orchestrates terraform apply (and destroy) exclusively via the Terraform MCP (Task 019)
- Performs no direct shell execution and generates no AWS credentials
- Only proceeds when the run has a recorded approval
- Does not modify the terraform state file directly
- Every action and outcome is recorded to the audit trail (who/what/when)
- Unit tests pass

## Out of Scope

CANNOT generate infrastructure or Terraform configuration; only orchestrates apply/destroy via the MCP. Does not implement the approval gate (Task 029) or the apply graph node (Task 035).

## Deliverables

src/cloudpilot/agents/deployment.py
tests/test_deployment_agent.py
