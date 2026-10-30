# Task 041 - Incident Detection

## Goal

Implement the MONITORING node that detects incidents and failures from CloudWatch metrics and alarms via the CloudWatch MCP. The node classifies anomalies and surfaces detected incidents into graph state.

## Inputs

Metrics and alarm state from the CloudWatch MCP (Task 039); deployed resource identifiers from graph state.

## Outputs

A MONITORING node that emits structured incident records when failures or anomalies are detected.

## Dependencies

Task 039

## Acceptance Criteria

- Node retrieves metrics and alarms via the CloudWatch MCP and evaluates them against incident criteria.
- Detected incidents are represented as pydantic models with severity and source context.
- Returns a clear no-incident result when metrics and alarms are nominal.
- The node performs read-only analysis and never executes shell commands directly.
- Each detection cycle and any detected incident are logged.
- Unit tests pass

## Out of Scope

Post-deploy verification (Task 040), automatic remediation, and notification/alerting delivery.

## Deliverables

cloudpilot/graph/nodes/incident.py
tests/test_incident.py
