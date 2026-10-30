# Task 019 - Terraform MCP Server

## Goal

Build an MCP server that exposes terraform `init`, `validate`, `fmt`, `plan`, `apply`, and `destroy`. This is the single sanctioned path for executing the Terraform CLI; the LLM never invokes shell directly, and `apply`/`destroy` require an explicit approval flag.

## Inputs

Terraform CLI; MCP server foundation (Task 007); generated Terraform project directory.

## Outputs

A Terraform MCP server exposing the terraform lifecycle operations as tools.

## Dependencies

Task 007

## Acceptance Criteria

- MCP server exposes `init`, `validate`, `fmt`, `plan`, `apply`, and `destroy` operations.
- `apply` and `destroy` are rejected unless an approval flag is provided.
- The Terraform CLI is invoked only through this server; no other component executes terraform.
- The state file is never modified outside of standard terraform operations, and AWS credentials are never generated.
- Every operation is logged.
- Unit tests pass

## Out of Scope

Does not author Terraform code (Task 020); does not implement the approval workflow UI/policy; does not orchestrate graph nodes (Tasks 022-024).

## Deliverables

cloudpilot/mcp/terraform_server.py
tests/test_terraform_mcp.py
