# Task 026 - Cost Agent

## Goal

Implement a single-responsibility Cost Agent that estimates the monthly cost of the planned infrastructure. It flags expensive resources so they can be surfaced during review.

## Inputs

Generated Terraform plan/configuration produced by Task 020.

## Outputs

Structured cost estimate (pydantic model) with per-resource and total monthly cost, and flags for expensive resources.

## Dependencies

Task 020

## Acceptance Criteria

- Produces an estimated monthly cost for the planned infrastructure
- Provides a per-resource cost breakdown
- Flags resources whose cost exceeds a configurable threshold
- Estimate is returned as a typed pydantic model
- Every review action is logged per docs/security.md
- Unit tests pass

## Out of Scope

Does not modify the Terraform; does not execute terraform; does not block deployment; does not perform real-time billing API calls beyond estimation.

## Deliverables

src/cloudpilot/agents/cost.py
tests/test_cost_agent.py
