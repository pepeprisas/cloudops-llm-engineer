# Task 017 - Requirement Extraction

## Goal

Implement the logic that extracts structured requirements from a natural-language request and populates the `DeploymentPlan`: the AWS services involved, their sizing, and the overall complexity. This feeds the Planner agent's structured output.

## Inputs

Natural-language request; Planner agent context (Task 015); `DeploymentPlan` schema.

## Outputs

Requirement-extraction module that produces structured service, sizing, and complexity data for the `DeploymentPlan`.

## Dependencies

Task 015

## Acceptance Criteria

- Extraction produces AWS services, sizing details, and a complexity estimate from a request.
- Extracted output validates against the `DeploymentPlan` schema.
- Handles requests with multiple services and partial sizing information.
- Extraction actions are logged.
- Unit tests pass

## Out of Scope

Does not detect or resolve ambiguity (Task 018); does not generate Terraform or deploy; does not run shell or generate AWS credentials.

## Deliverables

cloudpilot/agents/planner_extraction.py
tests/test_requirement_extraction.py
