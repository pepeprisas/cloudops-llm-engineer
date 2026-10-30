# Task 023 - Terraform Formatting Node

## Goal

Implement the graph node that runs terraform `fmt` via the Terraform MCP on the generated code. This normalizes generated HCL formatting before validation and planning.

## Inputs

Generated `TerraformProject` (Task 020); Terraform MCP `fmt` operation (Task 019); graph state.

## Outputs

A formatting node that applies terraform `fmt` and updates graph state with the result.

## Dependencies

Task 019
Task 020

## Acceptance Criteria

- Node runs terraform `fmt` through the Terraform MCP.
- No direct shell execution (invoked via Terraform MCP).
- Formatted output replaces the generated project files.
- Formatting result is reflected in graph state.
- Formatting actions are logged.
- Unit tests pass

## Out of Scope

Does not validate (Task 022) or plan (Task 024); does not apply or destroy; does not generate Terraform or invoke the CLI directly.

## Deliverables

cloudpilot/graph/nodes/format.py
tests/test_format_node.py
