# Task 021 - Terraform Templates

## Goal

Create reusable HCL templates, rendered with jinja2, one per supported AWS service. These templates are consumed by the Terraform agent to assemble a `TerraformProject`.

## Inputs

Terraform agent rendering interface (Task 020); per-service configuration from the `DeploymentPlan`.

## Outputs

A directory of jinja2 HCL templates covering the supported AWS services.

## Dependencies

Task 020

## Acceptance Criteria

- jinja2 HCL templates exist for each supported AWS service.
- Templates render to valid HCL given service configuration variables.
- Template variables map cleanly onto `DeploymentPlan` service fields.
- Rendered output is consumable by the Terraform agent.
- Unit tests pass

## Out of Scope

Does not implement agent logic (Task 020); does not execute terraform validate/fmt/plan (Tasks 022-024); contains no shell execution.

## Deliverables

src/cloudpilot/agents/templates/
tests/test_terraform_templates.py
