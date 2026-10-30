# Task 007 - AWS Authentication

## Goal

Provide AWS authentication using boto3 sessions and role assumption. The module reads ambient or assumed credentials only and never generates credentials, producing least-privilege sessions for MCP servers.

## Inputs

`Settings` from Task 004 (region, role ARN, profile) and ambient AWS credentials from the environment.

## Outputs

A module exposing boto3 session/client factories that use ambient or assumed-role credentials.

## Dependencies

Task 004

## Acceptance Criteria

- Provides a function returning a configured `boto3.Session` from ambient credentials or an assumed role
- NEVER generates, mints, or persists AWS credentials; only reads ambient/assumed ones (per docs/security.md)
- Role assumption uses STS `assume_role` with a scoped session for least privilege
- Region and role configuration come from `Settings`
- Credentials are never logged (integrates with the logging module's redaction)
- Failure modes (missing credentials, failed assume-role) raise clear, typed errors
- Unit tests pass (boto3/STS mocked, e.g. via moto or stubber)

## Out of Scope

Defining IAM policies/roles themselves and MCP server business logic.

## Deliverables

cloudpilot/core/aws.py
tests/test_aws.py
