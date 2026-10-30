# Task 015 - Planner Agent

## Goal

Build an LLM agent that converts a natural-language request into a `DeploymentPlan`: identifying the required AWS services, estimating complexity, and detecting ambiguity. The agent uses the LLM agent abstraction and emits a validated `DeploymentPlan`.

## Inputs

Natural-language deployment request; `DeploymentPlan` schema (Task 014); LLM agent abstraction (Task 049).

## Outputs

A Planner agent that returns a populated, validated `DeploymentPlan`.

## Dependencies

Task 014
Task 049

## Acceptance Criteria

- Planner agent accepts a natural-language request and returns a validated `DeploymentPlan`.
- Agent identifies AWS services, estimates complexity, and flags ambiguities in the request.
- Agent uses the shared LLM agent abstraction rather than calling the model client directly.
- Every planning action is logged.
- Unit tests pass

## Out of Scope

Planner Agent CANNOT generate Terraform and CANNOT deploy. Does not run shell, does not generate AWS credentials, and does not author prompt content (Task 016) or the extraction/clarification logic (Tasks 017, 018).

## Deliverables

src/cloudpilot/agents/planner.py
tests/test_planner_agent.py
