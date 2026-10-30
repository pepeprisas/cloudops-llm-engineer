# Task 020 - Terraform Agent

## Goal

Build an LLM agent that converts a `DeploymentPlan` into a `TerraformProject` with a standard project structure. The agent generates Terraform code only; it never executes any terraform command.

## Inputs

`DeploymentPlan` (Task 014); LLM agent abstraction (Task 009).

## Outputs

A Terraform agent that produces a `TerraformProject` (standard directory/file structure with generated HCL).

## Dependencies

Task 014
Task 009

## Acceptance Criteria

- Agent accepts a `DeploymentPlan` and produces a `TerraformProject` with a standard structure.
- Generated project includes the expected files for the planned AWS services.
- Agent uses the shared LLM agent abstraction.
- Generation actions are logged.
- Unit tests pass

## Out of Scope

Terraform Agent CANNOT apply and CANNOT plan; it performs no shell execution. Does not run terraform (Terraform MCP, Task 019), does not author the HCL templates (Task 021), and does not generate AWS credentials.

## Deliverables

cloudpilot/agents/terraform.py
tests/test_terraform_agent.py
