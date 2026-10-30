# AI Systems Specification

## Purpose

Provide platform- and language-independent criteria for designing and evaluating
software that uses language models, AI agents, retrieval, memory, or model-driven
tools.

AI behavior is probabilistic. Safety and correctness boundaries must therefore
be enforced by deterministic application code where possible.

## Define the AI Boundary

Before designing an AI-powered feature:

- Identify which behavior requires a model and which behavior should remain
  deterministic.
- Define the model's inputs, outputs, available context, and permitted actions.
- Identify trusted and untrusted data crossing the boundary.
- Define the consequences of incorrect, malformed, delayed, or absent output.
- Establish latency, cost, privacy, and quality requirements.
- Prefer a simpler deterministic implementation when it adequately satisfies the
  requirement.

Do not use a model as the sole enforcement mechanism for authorization,
validation, safety policy, or data integrity.

## Models and Providers

Consider:

- Required model capabilities and supported input or output modalities.
- Provider-specific APIs, limits, error behavior, and content handling.
- Model and prompt versioning.
- Context-window and output-token limits.
- Rate limits, quotas, latency, and cost.
- Data retention, training, residency, and privacy policies.
- Portability requirements and the value of a provider abstraction.

An abstraction should represent capabilities the application actually needs. It
should not hide meaningful provider differences behind a misleadingly uniform
interface.

## Prompt Construction

Prompts should:

- Separate trusted instructions from untrusted content.
- Clearly identify the task, available context, constraints, and output format.
- Avoid including unnecessary secrets or personal data.
- Define behavior for missing, conflicting, or insufficient information.
- Remain within a measured context budget.
- Be versioned or otherwise traceable when behavior depends on them.

Treat user input, retrieved documents, web content, tool output, conversation
history, and stored memory as untrusted data rather than privileged
instructions.

## Structured Output

When application logic consumes model output:

- Define an explicit schema.
- Parse and validate the output before use.
- Reject unknown or dangerous values where appropriate.
- Handle missing fields, malformed data, refusals, and truncated responses.
- Distinguish repairable formatting problems from semantic invalidity.
- Bound any repair or retry loop.
- Preserve the original failure context for diagnosis without exposing sensitive
  content.

A successful parse does not prove that the output is factually or semantically
correct.

## Tools and Actions

For every model-accessible tool:

- Define a narrow purpose and typed input contract.
- Validate and authorize inputs in application code.
- Apply least privilege to files, data, networks, and external services.
- Bound execution time, output size, and resource use.
- Define whether the operation is read-only, idempotent, reversible, or
  destructive.
- Require confirmation for consequential actions when appropriate.
- Return errors in a form the application can handle safely.
- Record sufficient audit information without logging secrets.

The model must not be able to expand its own permissions or bypass tenant,
resource, or user authorization.

## Agent Control Flow

Agent workflows should define:

- Entry and completion conditions.
- Maximum steps, tool calls, retries, time, and cost.
- Allowed transitions and handoff rules.
- State ownership and persistence.
- Behavior for repeated actions and duplicate tool requests.
- Handling for tool failure, model refusal, cancellation, and timeout.
- A safe outcome when the agent cannot complete the task.

Prevent unbounded loops, recursive delegation, and retry of non-idempotent
actions without deduplication or confirmation.

## Context, Memory, and Retrieval

Consider:

- Which information is needed for the current task.
- Token budgeting and deterministic truncation behavior.
- User, tenant, session, and conversation isolation.
- Authorization filters applied during retrieval.
- The provenance and freshness of retrieved information.
- Retention, deletion, and correction of stored memory.
- Whether summaries preserve critical facts and uncertainty.
- Poisoning or instruction injection through stored and retrieved content.

Do not treat semantic similarity as authorization or factual verification.

## Reliability and Failure Handling

Define behavior for:

- Provider unavailability and rate limiting.
- Timeouts and cancellation.
- Partial or interrupted streaming.
- Invalid or empty responses.
- Context-length and content-policy errors.
- Retryable versus permanent failures.
- Fallback models or degraded operation.
- Duplicate execution caused by retries or replay.

Use bounded retries with backoff where appropriate. Do not retry a consequential
operation unless its idempotency behavior is understood.

## Evaluation and Testing

Use deterministic tests for:

- Prompt assembly and context selection.
- Schema validation and output parsing.
- Tool authorization and argument validation.
- State transitions and termination conditions.
- Retry, timeout, cancellation, and fallback behavior.
- Tenant and conversation isolation.

Use recorded responses, fakes, or contract tests where they preserve meaningful
provider behavior. Do not make ordinary tests depend on exact natural-language
wording from a live model.

Model-based evaluations should define:

- Representative inputs and failure cases.
- Measurable acceptance criteria.
- The model, prompt, parameters, and dataset versions.
- Repetition or statistical treatment for nondeterministic results.
- Human review requirements for subjective judgments.

## Observability

Capture enough information to diagnose:

- Model and prompt versions.
- Request duration, token use, and cost.
- Retries, refusals, parsing failures, and tool failures.
- Agent transitions and termination reasons.
- Retrieval sources and tool invocation identifiers.

Redact secrets and sensitive content. Prefer structured metadata and correlation
identifiers over logging complete prompts, responses, or user data.

## AI Design Advice Output

AI-system advice should include:

1. Deterministic and model-driven responsibilities.
2. Model inputs, outputs, context, and validation.
3. Tool permissions and consequential actions.
4. Agent control flow, limits, and failure behavior.
5. State, retrieval, privacy, and isolation requirements.
6. Evaluation and observability strategy.
7. Assumptions, provider dependencies, risks, and unresolved decisions.

Report only sections relevant to the proposed feature.
