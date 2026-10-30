# Task 014 - DeploymentPlan Schema

## Goal

Define the `DeploymentPlan` pydantic models that capture the requested AWS services, estimated complexity, detected ambiguities, and clarifications. This schema is the formal contract between the Planner agent and the Terraform agent.

## Inputs

None (consumes the data shapes established in Task 008)

## Outputs

`DeploymentPlan` pydantic models and supporting sub-models (AWS services, complexity rating, ambiguities, clarifications).

## Dependencies

Task 008

## Acceptance Criteria

- `DeploymentPlan` pydantic model defined with fields for AWS services, complexity, ambiguities, and clarifications.
- Sub-models for individual AWS services and clarification items are defined and typed.
- Model validates required vs. optional fields and rejects malformed input.
- Model serializes to and deserializes from JSON round-trip without loss.
- Unit tests pass

## Out of Scope

Does not populate the plan from a request (Planner agent, Task 015); does not generate Terraform; does not perform any LLM calls or AWS interactions.

## Deliverables

src/cloudpilot/models/deployment_plan.py
tests/test_deployment_plan.py
