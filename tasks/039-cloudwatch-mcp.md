# Task 039 - CloudWatch MCP

## Goal

Implement an MCP server that exposes AWS CloudWatch capabilities (logs, metrics, alarms, and health) to CloudPilot agents and graph nodes. The server provides read access to observability data needed for post-deploy verification and incident detection.

## Inputs

AWS read-only configuration/credentials provided by the runtime (Task 007); CloudWatch MCP contract (docs/mcp/mcp-cloudwatch.md).

## Outputs

A running CloudWatch MCP server exposing logs/metrics/alarms/health tools.

## Dependencies

Task 007

## Acceptance Criteria

- Server exposes tools for querying CloudWatch logs, metrics, alarms, and health/service status.
- All tool inputs and outputs are validated with pydantic models.
- The server never generates AWS credentials and uses only the runtime-provided read-only context.
- Every tool invocation is logged with its parameters and result status.
- The server performs no mutating AWS operations (read-only).
- Unit tests pass

## Out of Scope

Mutating CloudWatch resources (creating/deleting alarms), and consuming nodes (verification, incident detection) which are separate tasks.

## Deliverables

src/cloudpilot/mcp/cloudwatch_server.py
tests/test_cloudwatch_mcp.py
