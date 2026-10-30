# Application Security Specification

## Purpose

Provide platform- and language-independent criteria for designing and evaluating
the security of AI-powered applications and agent workflows.

Apply this specification together with the relevant workflow, domain, and
language specifications. Security controls must be enforced by deterministic
application and infrastructure boundaries rather than model instructions alone.

## Establish Security Context

Before recommending or evaluating a change:

- Identify protected assets and sensitive operations.
- Identify users, tenants, services, agents, and external actors.
- Map trust boundaries and untrusted inputs.
- Determine authentication and authorization mechanisms.
- Identify tools, data stores, model providers, and external services.
- Review deployment and network exposure where relevant.
- Identify credible abuse cases and the impact of compromise.

State assumptions when production configuration or surrounding controls cannot
be verified.

## Prompt Injection and Untrusted Content

Treat the following as untrusted data:

- User messages and uploaded files.
- Retrieved documents and vector-store content.
- Web pages and external API responses.
- Tool results and third-party service output.
- Conversation history and stored memory.
- Model-generated content.

Check that untrusted content cannot:

- Override trusted application policy.
- Expand model or agent permissions.
- Bypass authorization or approval requirements.
- Cause unauthorized data access or disclosure.
- Trigger unsafe tools or consequential actions.
- Persist malicious instructions into future contexts.

Prompt wording may reduce accidental behavior, but it is not a security boundary.

## Tools and Privileged Actions

For every tool or model-driven action:

- Define a narrow, validated input contract.
- Enforce user, tenant, and resource authorization in application code.
- Apply least privilege to files, networks, data, and external services.
- Restrict commands, paths, URLs, and operations to the required scope.
- Bound execution time, output size, and resource consumption.
- Classify the action as read-only, reversible, consequential, or destructive.
- Require confirmation or policy approval where appropriate.
- Record auditable outcomes without exposing secrets.
- Prevent the model from modifying its own permissions or tool definitions.

Treat model-generated tool arguments as untrusted input.

## Secrets and Sensitive Data

Check for:

- Secrets embedded in source code, prompts, fixtures, or configuration.
- Credentials exposed through logs, traces, exceptions, or tool output.
- Sensitive data sent unnecessarily to model or service providers.
- Excessive retention of prompts, responses, files, or agent memory.
- Missing redaction in observability and evaluation data.
- Insecure secret loading, storage, rotation, or propagation.
- Cross-user or cross-tenant exposure through caches, retrieval, or history.

Collect and expose only the information required for the operation.

## Input and Output Handling

Validate untrusted input and model-generated output before use.

Consider:

- SQL, command, template, and expression injection.
- Path traversal and unauthorized file access.
- Server-side request forgery.
- Unsafe deserialization.
- Cross-site scripting and unsafe rendered model output.
- Missing schema validation for structured output.
- Dangerous URLs, identifiers, or tool arguments.
- Resource-exhaustion inputs and unbounded payloads.
- Trusting generated code or instructions without isolation and approval.

A syntactically valid model response is not automatically safe or authorized.

## Authentication, Authorization, and Isolation

Check that:

- Authentication is required at the correct boundary.
- Authorization is enforced for each resource and action.
- User, tenant, session, and conversation identifiers cannot be substituted.
- Background work and agent handoffs preserve the initiating security context.
- Retrieval and persistence queries enforce isolation.
- Administrative operations require appropriate privilege and confirmation.
- Denied operations fail closed without leaking sensitive information.
- Service credentials cannot be used to bypass user-level authorization.

Authentication alone does not authorize access to every resource.

## Network and Dependency Security

Where relevant, consider:

- Outbound network allowlists or equivalent restrictions.
- Validation of user- or model-supplied URLs.
- Access to internal services, metadata endpoints, and private address ranges.
- TLS verification and certificate rotation.
- Dependency provenance, maintenance, and known vulnerabilities.
- Integrity of model, prompt, plugin, and tool packages.
- Secure defaults for externally exposed services.
- Rate limiting and abuse controls.

New dependencies and network access should be justified by the requested
behavior.

## Errors, Logging, and Observability

Check that:

- Errors do not reveal credentials, internal prompts, or sensitive records.
- Security-relevant denials and consequential actions are auditable.
- Logs distinguish users, tenants, requests, tools, and agent runs safely.
- Redaction occurs before data reaches external logging or tracing systems.
- Detection signals exist for repeated denials, unusual tool use, and abuse.
- Audit records are protected from unauthorized modification.

Avoid logging complete prompts or responses by default.

## Security Validation

Use relevant deterministic validation such as:

- Unit tests for authorization, validation, and policy decisions.
- Integration tests across real security boundaries.
- Tenant-isolation and cross-resource access tests.
- Tool allowlist and argument-validation tests.
- Prompt-injection scenarios that verify deterministic controls.
- Static analysis, dependency analysis, and secret scanning.
- Negative tests for unsafe URLs, paths, payloads, and generated output.

Do not treat a model refusal or a successful prompt-based attack simulation as
proof of a complete security boundary.

## Security Advice and Review Output

Build-time security advice should include:

1. Assets, actors, trust boundaries, and abuse cases.
2. Required authorization and isolation controls.
3. Tool, input, output, network, and data protections.
4. Security validation strategy.
5. Assumptions, residual risks, and unresolved decisions.

Review findings must follow `specs/shared/finding-contract.md`, include concrete
evidence, and distinguish confirmed vulnerabilities from potential risks.

If no material issue is supported, state that explicitly rather than inventing
findings.
