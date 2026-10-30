# Build Workflow Specification

## Purpose

Define a controlled workflow for planning, implementing, and validating a scoped
change in an existing software project.

This workflow follows `specs/shared/workflow-principles.md`. Platform adapters
and language extensions may add operational detail without weakening its
constraints.

## Modes

### Plan Mode

Inspect the project, consult relevant advisors, and produce an implementation
plan. Do not modify project files.

### Execute Mode

Plan, implement, and validate the requested change. File modifications must have
one clearly designated implementation owner.

The selected mode must be explicit before implementation begins.

## Inputs

Establish the following before planning:

- Requested outcome.
- Relevant functional and nonfunctional requirements.
- Acceptance criteria, when provided.
- Intended scope and explicit exclusions.
- Project instructions and engineering conventions.
- Approval requirements for risky, destructive, or scope-expanding actions.

Ask for clarification when a missing input could materially change the design,
scope, safety, or expected result. Otherwise, state reasonable assumptions.

## Roles

### Build Supervisor

The build supervisor:

- Establishes context and scope.
- Selects relevant advisors.
- Produces or consolidates the implementation plan.
- Ensures that one implementation owner performs file modifications.
- Coordinates validation.
- Reports results, limitations, and unresolved risks.

### Advisors

Advisors provide focused, read-only analysis. They do not modify project files.

Relevant advisory areas may include:

- Architecture and service boundaries.
- AI models, prompts, tools, and agent behavior.
- Application security.
- Data integrity, persistence, and privacy.
- Reliability, observability, and testing.
- Language- or framework-specific engineering.

Advisors should be selected based on the requested behavior and affected code,
not invoked merely to increase apparent coverage.

### Implementation Owner

The implementation owner:

- Applies the approved or established plan.
- Keeps changes within scope.
- Preserves existing user work.
- Follows project conventions.
- Adds or updates relevant validation.
- Does not commit or publish changes without explicit authorization.

## Workflow

### Phase 1: Establish Project Context

1. Read applicable project instructions and documentation.
2. Inspect repository status before modifying files.
3. Identify the relevant components, dependencies, tests, and configuration.
4. Distinguish pre-existing changes from work required by the request.
5. Identify available deterministic validation tools.

### Phase 2: Define the Outcome

1. Restate the requested behavior.
2. Identify acceptance criteria.
3. Record assumptions and open questions.
4. Define what is out of scope.
5. Identify compatibility, migration, or deployment constraints.

Do not begin implementation while material ambiguity remains unresolved.

### Phase 3: Analyze Impact

1. Trace the affected execution paths and interfaces.
2. Search for callers, consumers, related patterns, and existing tests.
3. Identify security, data, reliability, and operational implications.
4. Consult only the advisors relevant to those implications.
5. Preserve meaningful advisor disagreement or uncertainty.

### Phase 4: Plan the Change

The implementation plan should describe:

- Files or components expected to change.
- Intended behavior and design decisions.
- Interface, schema, configuration, or dependency changes.
- Error handling and failure behavior.
- Tests and other validation to add or run.
- Risks, alternatives, and rollback considerations where relevant.

In Plan Mode, stop after presenting the plan.

### Phase 5: Implement

1. Assign one implementation owner.
2. Make the smallest coherent change that satisfies the requirements.
3. Follow existing architecture, naming, typing, and error-handling conventions.
4. Avoid unrelated refactoring and formatting churn.
5. Add or update tests for important behavior and failure paths.
6. Reassess the plan if implementation reveals a material new constraint.

Obtain approval before materially expanding scope or performing a destructive or
irreversible action.

### Phase 6: Validate

1. Inspect the resulting diff for scope and accidental changes.
2. Run the most focused relevant tests first.
3. Run applicable formatting, linting, type checking, security, or broader test
   commands when justified by the change.
4. Verify acceptance criteria and important failure paths.
5. Report commands that were not run and explain why.
6. Do not claim success when validation failed or was incomplete.

### Phase 7: Independent Review

When requested or required:

1. Provide the review workflow with the implemented diff, requirements,
   assumptions, and validation results.
2. Keep reviewers read-only.
3. Validate review findings before treating them as defects.
4. Obtain approval before applying revisions that expand scope or alter agreed
   behavior.
5. Re-run relevant validation after revisions.

## Stop Conditions

Pause and request user direction when:

- Material requirements remain ambiguous.
- Required access or permissions are unavailable.
- A destructive or irreversible action is necessary.
- A secret or sensitive value would need to be exposed.
- The required change substantially exceeds the agreed scope.
- Validation reveals failures that cannot be safely resolved within scope.

## Completion Report

An Execute Mode completion report should include:

1. Outcome summary.
2. Files changed and the purpose of each change.
3. Validation commands and results.
4. Acceptance criteria that were verified.
5. Advisor and review coverage.
6. Unresolved risks, limitations, or unverified behavior.
7. Follow-up work, if any.

A Plan Mode report should include the proposed design, expected file changes,
validation strategy, assumptions, risks, and open decisions.
