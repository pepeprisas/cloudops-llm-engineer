# Task 024 - Terraform Plan Node

## Goal

Implement the graph node that runs terraform `plan` via the Terraform MCP and parses the plan output into graph state. This produces the change preview used for downstream review and approval.

## Inputs

Generated `TerraformProject` (Task 020); Terraform MCP `plan` operation (Task 019); graph state.

## Outputs

A plan node that runs terraform `plan` and writes a parsed plan summary into graph state.

## Dependencies

Task 019
Task 020

## Acceptance Criteria

- Node runs terraform `plan` through the Terraform MCP.
- No direct shell execution (invoked via Terraform MCP).
- Plan output is parsed into a structured summary in graph state.
- Plan errors are surfaced back into state for routing.
- Plan actions are logged.
- Unit tests pass

## Out of Scope

Does not apply or destroy and does not bypass approval; does not validate (Task 022) or format (Task 023); does not generate Terraform or invoke the CLI directly.

## Deliverables

src/cloudpilot/graph/nodes/plan.py
tests/test_plan_node.py
