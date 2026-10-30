# Task 049 - LLM Agent Abstraction

## Goal

Build the shared LLM agent abstraction that every CloudPilot agent uses instead of calling a model client directly. It owns prompt assembly, schema-validated generation, and the hard capability limits that keep an agent inside its role.

## Inputs

Package layout and pydantic (Task 001); settings for timeouts and retry limits (Task 004).

## Outputs

A provider-narrow LLM client in `src/cloudpilot/core/` with a typed per-role configuration, and a schema-validating `generate()` that returns a discriminated result rather than a bare value.

## Dependencies

Task 001
Task 004

## Acceptance Criteria

- Lives in `core/` and is imported by agents; no agent imports a provider client directly.
- The per-role tool manifest is fixed at construction and immutable afterwards. No method, parameter, or config path lets model output add tools, widen scope, or select a different role.
- Approval-gated operations (`apply`, `destroy`, IAM, network mutation) are structurally absent from the model-facing surface — enforced by the registry, not by prompt wording.
- Generation validates against an explicit pydantic schema. A parsed result is exposed as an untrusted proposal, not as verified output; parse validity is never presented as correctness or authorization.
- Trusted system instructions are kept separate from untrusted content; user input, tool output, and retrieved content cannot mutate the system prompt, tool registry, or role config.
- Steps, tool calls, retries, time, and cost are bounded. Malformed output, refusal, timeout, and schema failure each surface as a typed failure and never as an implicit proceed.
- Retries apply to the model call only, never to tool invocation. Timeouts and retry limits come from settings; no client is constructed at import time.
- Unit tests use deterministic fakes; the default run makes no live model call.
- Unit tests pass

## Out of Scope

Planner and Terraform agent logic and prompts (Tasks 015, 016, 017, 018, 020, 021); MCP servers (Task 019); LangGraph nodes (Task 009); API routes (Task 010); the approval gate and audit trail (Tasks 029, 033), which this task references rather than implements. Streaming is omitted until a consumer requires it.

## Deliverables

src/cloudpilot/core/llm.py
tests/test_llm.py
