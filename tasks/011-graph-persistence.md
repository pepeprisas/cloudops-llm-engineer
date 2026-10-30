# Task 011 - Graph Persistence

## Goal

Wire a LangGraph checkpointer interface so graph runs are durable and resumable. This lets a deployment pause at the approval gate and resume later without losing state.

## Inputs

The compiled graph from Task 009 and `DeploymentState` from Task 008.

## Outputs

A persistence module exposing a checkpointer interface/factory the graph can be compiled with.

## Dependencies

Task 009

## Acceptance Criteria

- Defines a checkpointer interface/abstraction the graph compiles against
- The graph can be compiled with a checkpointer and run with a thread/run id
- A run can be interrupted (e.g. at approval) and resumed from its last checkpoint
- Backend is pluggable (concrete backend deferred to Task 012)
- Checkpoints never store AWS credentials or secrets
- Unit tests pass (resume-from-checkpoint with an in-memory checkpointer)

## Out of Scope

The concrete database-backed checkpointer (Task 012) and API wiring.

## Deliverables

src/cloudpilot/graph/persistence.py
tests/test_persistence.py
