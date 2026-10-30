# Task 018 - Clarification Questions

## Goal

Detect ambiguity in a deployment request and generate clarification questions, looping until the request is sufficiently resolved. This ensures the `DeploymentPlan` is built from an unambiguous specification.

## Inputs

Natural-language request and detected ambiguities; Planner agent context (Task 015); `DeploymentPlan` schema.

## Outputs

Clarification module that produces clarification questions and tracks resolution until ambiguity is cleared.

## Dependencies

Task 015

## Acceptance Criteria

- Module detects ambiguity in a request and generates targeted clarification questions.
- A loop continues requesting clarification until no unresolved ambiguity remains.
- Resolved clarifications are recorded in the `DeploymentPlan`.
- Clarification actions are logged.
- Unit tests pass

## Out of Scope

Does not perform requirement extraction (Task 017); does not generate Terraform or deploy; does not run shell or generate AWS credentials.

## Deliverables

cloudpilot/agents/clarify.py
tests/test_clarify.py
