# Task 040 - Health Checks

## Goal

Implement the VERIFYING graph node that performs post-deployment health checks using the CloudWatch MCP. The node confirms deployed infrastructure is healthy and fails the run when health checks do not pass.

## Inputs

Deployment result/state from the apply step (Task 035); health/metrics/alarms data from the CloudWatch MCP (Task 039).

## Outputs

A VERIFYING node that updates graph state with a health verdict and fails the run on unhealthy results.

## Dependencies

Task 039
Task 035

## Acceptance Criteria

- Node queries health, alarms, and key metrics via the CloudWatch MCP for the deployed resources.
- Produces a structured, pydantic-validated health verdict in graph state.
- Run transitions to a failed/unhealthy outcome when health checks fail.
- The node does not modify the state file directly and does not bypass approval.
- Every health check and the final verdict are logged.
- Unit tests pass

## Out of Scope

Incident detection during ongoing monitoring (Task 041), remediation, and retry logic.

## Deliverables

src/cloudpilot/graph/nodes/verify.py
tests/test_verify.py
