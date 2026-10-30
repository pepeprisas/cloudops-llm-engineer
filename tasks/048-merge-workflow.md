# Task 048 - Merge Workflow

## Goal

Implement the graph node that merges the pull request after explicit human approval, via the GitHub MCP. Merging is the approval-gated step that promotes reviewed Terraform changes.

## Inputs

Open PR identifier from graph state (Task 046); human approval signal from the approval gate (Task 029); merge tooling from the GitHub MCP.

## Outputs

A node that merges the approved PR and records the merge outcome in graph state.

## Dependencies

Task 046
Task 029

## Acceptance Criteria

- Node merges the PR only after a valid human approval has been recorded.
- Merge is refused/blocked when approval is missing or invalid.
- Merge is performed via the GitHub MCP and never via direct shell/git.
- Merge outcome metadata is captured in pydantic-validated graph state.
- The approval check and merge action are logged.
- Unit tests pass

## Out of Scope

Generating or granting the approval itself (Task 029), and post-merge deployment steps.

## Deliverables

src/cloudpilot/graph/nodes/merge.py
tests/test_merge.py
