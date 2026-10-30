# Task 046 - Create PR

## Goal

Implement the graph node that opens a pull request containing the committed Terraform along with a plan and review summary, using the GitHub MCP. The PR becomes the human review surface for the deployment.

## Inputs

Committed Terraform branch metadata (Task 045); create-PR tooling from the GitHub MCP (Task 044); plan and review summaries from graph state.

## Outputs

A node that opens a PR and records the PR identifier/URL in graph state.

## Dependencies

Task 044
Task 045

## Acceptance Criteria

- Node opens a PR from the working branch via the GitHub MCP.
- PR body includes the Terraform plan summary and review summary.
- PR identifier and URL are captured in pydantic-validated graph state.
- The node does not merge the PR and does not bypass approval.
- The PR creation action is logged.
- Unit tests pass

## Out of Scope

Posting individual review comments (Task 047) and merging the PR (Task 048).

## Deliverables

src/cloudpilot/graph/nodes/pr.py
tests/test_pr.py
