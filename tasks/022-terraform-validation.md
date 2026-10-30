# Task 022 - Terraform Validation Node

## Goal

Implement the VALIDATING graph node that runs terraform `validate` via the Terraform MCP against the generated project and surfaces any errors back into the graph state. This gives the state machine a verified-or-failed signal for generated code.

## Inputs

Generated `TerraformProject` (Task 020); Terraform MCP `validate` operation (Task 019); graph state.

## Outputs

A VALIDATING node that updates graph state with validation results and surfaced errors.

## Dependencies

Task 019
Task 020

## Acceptance Criteria

- Node runs terraform `validate` through the Terraform MCP.
- No direct shell execution (invoked via Terraform MCP).
- Validation errors are parsed and written back into graph state.
- Node sets a clear pass/fail outcome for downstream routing.
- Validation actions are logged.
- Unit tests pass

## Out of Scope

Does not format (Task 023) or plan (Task 024); does not apply or destroy; does not generate Terraform or invoke the CLI directly.

## Deliverables

src/cloudpilot/graph/nodes/validate.py
tests/test_validate_node.py
