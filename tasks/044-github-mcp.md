# Task 044 - GitHub MCP

## Goal

Implement an MCP server that exposes GitHub operations (create PR, create issue, commit, comment, and review) to CloudPilot graph nodes. The server provides the integration surface for the PR-based deployment workflow.

## Inputs

GitHub access configuration/token provided by the runtime (Task 004); GitHub MCP contract (docs/mcp/mcp-github.md).

## Outputs

A running GitHub MCP server exposing create PR/issue, commit, comment, and review tools.

## Dependencies

Task 004

## Acceptance Criteria

- Server exposes tools for create PR, create issue, commit, comment, and review.
- All tool inputs and outputs are validated with pydantic models.
- The server does not expose a direct merge operation that bypasses approval gating.
- The server never generates AWS credentials and never executes shell directly.
- Every tool invocation is logged with its parameters and result status.
- Unit tests pass

## Out of Scope

Merge workflow (Task 048) and the specific consuming nodes (commit, PR, review comments) which are separate tasks.

## Deliverables

cloudpilot/mcp/github_server.py
tests/test_github_mcp.py
