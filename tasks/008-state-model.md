# Task 008 - State Model

## Goal

Define the `DeploymentState` model and a status enum that match the LangGraph state machine. This is the shared data structure threaded through every node of the graph.

## Inputs

`cloudpilot/graph/` package from Task 001.

## Outputs

A pydantic `DeploymentState` model and a `DeploymentStatus` enum.

## Dependencies

Task 001

## Acceptance Criteria

- `DeploymentStatus` enum includes: `REQUEST_RECEIVED`, `PLANNING`, `GENERATING_TERRAFORM`, `VALIDATING`, `SECURITY_REVIEW`, `COST_REVIEW`, `WAITING_FOR_APPROVAL`, `DEPLOYING`, `VERIFYING`, `MONITORING`, `COMPLETED`
- `DeploymentState` is a pydantic model carrying request text, status, plan/terraform artifacts, review results, approval decision, and an audit/event log
- The model is JSON-serializable for checkpointing
- Sensible defaults so a fresh state can be created from just a request
- Includes a deployment id and timestamps
- Unit tests pass (serialization round-trip, enum completeness)

## Out of Scope

Graph node logic and persistence backends.

## Deliverables

cloudpilot/graph/state.py
tests/test_state.py
