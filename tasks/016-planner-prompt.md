# Task 016 - Planner Prompt

## Goal

Author the system prompt and few-shot examples that drive the Planner agent. The prompt instructs the model to produce a structured `DeploymentPlan` and demonstrates correct behavior through worked examples.

## Inputs

Planner agent interface (Task 015); `DeploymentPlan` schema fields.

## Outputs

System prompt string and few-shot example set for the Planner agent.

## Dependencies

Task 015

## Acceptance Criteria

- System prompt defines the Planner role, output format, and constraints (service identification, complexity, ambiguity).
- At least two few-shot examples demonstrate request-to-`DeploymentPlan` mapping.
- Prompt explicitly states the Planner does not generate Terraform or deploy.
- Prompt content is importable and consumed by the Planner agent.
- Unit tests pass

## Out of Scope

Does not implement agent control flow (Task 015); does not perform extraction or clarification logic; contains no executable AWS or shell behavior.

## Deliverables

src/cloudpilot/agents/prompts/planner.py
tests/test_planner_prompt.py
