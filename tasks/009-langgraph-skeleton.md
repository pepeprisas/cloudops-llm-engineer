# Task 009 - LangGraph Skeleton

## Goal

Build the LangGraph `StateGraph` with one node per deployment state and linear edges connecting them. Node logic is stubbed so the graph compiles and runs end-to-end with placeholders.

## Inputs

`DeploymentState` and `DeploymentStatus` from Task 008.

## Outputs

A compiled `StateGraph` with a node per state, linear edges, and a builder/factory function.

## Dependencies

Task 008

## Acceptance Criteria

- One node exists per `DeploymentStatus` state, each advancing the state and updating status
- Edges are linear from `REQUEST_RECEIVED` through `COMPLETED`
- The graph compiles via a factory function and runs end-to-end on a sample request with placeholders
- Each node appends an entry to the audit/event log (per docs/security.md: every action logged)
- Stub nodes contain no real shell/AWS execution
- Unit tests pass (compilation + end-to-end placeholder run reaches `COMPLETED`)

## Out of Scope

Real agent/MCP node implementations, persistence, conditional/approval branching logic.

## Deliverables

src/cloudpilot/graph/graph.py
tests/test_graph.py
