# Task 047 - Review Comments

## Goal

Implement the graph node that posts security, cost, and best-practice findings as pull request review comments via the GitHub MCP. The node makes automated review results visible inline on the PR for human reviewers.

## Inputs

Open PR identifier from graph state (Task 046); review findings (security, cost, best-practice) from the review stage (Task 025); comment/review tooling from the GitHub MCP.

## Outputs

A node that posts review comments to the PR and records comment metadata in graph state.

## Dependencies

Task 046
Task 025

## Acceptance Criteria

- Node posts security, cost, and best-practice findings as PR review comments via the GitHub MCP.
- Findings are mapped to comments using pydantic-validated structures.
- Handles the empty-findings case without posting spurious comments.
- The node does not merge or approve the PR and does not bypass approval.
- Each posted comment is logged.
- Unit tests pass

## Out of Scope

Opening the PR (Task 046) and merging the PR (Task 048).

## Deliverables

src/cloudpilot/graph/nodes/review_comments.py
tests/test_review_comments.py
