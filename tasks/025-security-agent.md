# Task 025 - Security Agent

## Goal

Implement a single-responsibility Security Agent that reviews generated Terraform for security issues. It detects public exposure, over-broad IAM, and unencrypted resources, and produces structured findings for the review stage of the graph.

## Inputs

Generated Terraform plan/configuration produced by Task 020.

## Outputs

Structured security findings (pydantic model) describing each issue, its severity, and the affected resource.

## Dependencies

Task 020

## Acceptance Criteria

- Detects public exposure (e.g., open security groups, public S3/buckets, 0.0.0.0/0 ingress)
- Detects over-broad IAM (wildcard actions/resources, admin-equivalent policies)
- Detects unencrypted resources (volumes, buckets, databases without encryption)
- Findings are returned as a typed pydantic model with severity and resource references
- Every review action is logged per docs/security.md
- Unit tests pass

## Out of Scope

Does not modify or remediate the Terraform; does not execute terraform; does not approve or block deployment by itself.

## Deliverables

cloudpilot/agents/security.py
tests/test_security_agent.py
