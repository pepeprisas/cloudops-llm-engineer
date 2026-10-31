# Task 010 - API Layer

## Goal

Build the FastAPI application that is the User to FastAPI to LangGraph entry point. It exposes endpoints to submit a deployment request and to get status, approve, reject, and cancel a deployment.

## Inputs

The compiled graph from Task 009 and `DeploymentState` from Task 008.

## Outputs

A FastAPI app with routes wired to the LangGraph state machine.

## Dependencies

Task 009

## Acceptance Criteria

- Endpoints: submit request (create deployment), get status, approve, reject, cancel
- Submit returns a deployment id; status returns current `DeploymentStatus` and key state
- Approve/reject act on the human-in-the-loop approval gate; cancel halts a run
- Request/response bodies are validated pydantic models
- A health-check endpoint is provided
- Approval cannot be bypassed via the API (per the AGENTS.md hard rules)
- Every endpoint action is logged
- Unit tests pass (TestClient covering each route)

## Out of Scope

AuthN/AuthZ, rate limiting, and the concrete graph node business logic.

## Deliverables

src/cloudpilot/api/app.py
src/cloudpilot/api/routes.py
tests/test_api.py
