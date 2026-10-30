# Task 043 - Deployment Report

## Goal

Implement the agent that generates the final deployment report, aggregating the plan, reviews, cost estimate, deployment outcome, and post-deploy health results into a single structured document.

## Inputs

Cost estimation output (Task 026); health verdict from the VERIFYING node (Task 040); plan, reviews, and outcome from graph state.

## Outputs

A structured deployment report artifact summarizing the full run.

## Dependencies

Task 026
Task 040

## Acceptance Criteria

- Report aggregates plan, security/cost/best-practice reviews, cost estimate, deployment outcome, and health results.
- Report is produced as a pydantic-validated model with a human-readable rendering.
- Handles missing optional sections (e.g., skipped health checks) gracefully.
- Report generation is read-only and does not modify the state file.
- Report generation is logged.
- Unit tests pass

## Out of Scope

Delivering the report to external channels (PR comments, email), and report persistence/storage.

## Deliverables

src/cloudpilot/agents/report.py
tests/test_report.py
