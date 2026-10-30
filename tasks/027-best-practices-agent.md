# Task 027 - Best Practices Agent

## Goal

Implement a single-responsibility Best Practices Agent that checks generated Terraform against AWS and Terraform best practices and conventions. It produces findings highlighting deviations for the review stage.

## Inputs

Generated Terraform plan/configuration produced by Task 020.

## Outputs

Structured best-practices findings (pydantic model) describing each deviation and the affected resource.

## Dependencies

Task 020

## Acceptance Criteria

- Checks adherence to AWS best practices (tagging, naming, resource configuration)
- Checks adherence to Terraform conventions (module structure, variable usage, provider pinning)
- Findings are returned as a typed pydantic model with affected resource references
- Every review action is logged per docs/security.md
- Unit tests pass

## Out of Scope

Does not modify or remediate the Terraform; does not execute terraform; does not perform security or cost analysis (handled by Tasks 025 and 026).

## Deliverables

cloudpilot/agents/best_practices.py
tests/test_best_practices_agent.py
