# Task 045 - Commit Terraform

## Goal

Implement the graph node that commits generated Terraform to a target repository via the GitHub MCP. The node packages the generated configuration into a branch/commit ready for a pull request.

## Inputs

Generated Terraform configuration (Task 020); commit tooling from the GitHub MCP (Task 044).

## Outputs

A node that creates a commit (on a working branch) containing the generated Terraform and records commit metadata in graph state.

## Dependencies

Task 044
Task 020

## Acceptance Criteria

- Node commits the generated Terraform to a non-default working branch via the GitHub MCP.
- Commit metadata (branch, SHA, files) is captured in pydantic-validated graph state.
- The node never executes shell/git directly and uses only the GitHub MCP.
- The node does not modify the state file directly and does not bypass approval.
- The commit action is logged.
- Unit tests pass

## Out of Scope

Opening the pull request (Task 046), posting review comments (Task 047), and merging (Task 048).

## Deliverables

src/cloudpilot/graph/nodes/commit.py
tests/test_commit.py
