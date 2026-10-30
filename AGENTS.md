# Project Engineering Instructions

## Project

Build **CloudPilot**, a Python application that turns natural-language requests into reviewed AWS infrastructure deployments, using the AI Engineering Toolkit specifications.

`specs/` and `.opencode/` are vendored from ai-engineering-toolkit. Treat them as read-only inputs: apply them, do not fork or weaken them.

## Before implementation

1. Inspect the repository and existing project conventions.
2. Read `specs/shared/workflow-principles.md` and `specs/workflows/build/workflow.md`.
3. Read the relevant domain and Python guidance.
4. Read `docs/security.md` and the applicable `docs/agents/*.md` before touching anything that reaches AWS.
5. Clarify ambiguous requirements before making significant design decisions.
6. Propose a plan with scope, design decisions, files to change, and acceptance criteria.

## Hard rules

These override convenience. They hold in every implementation.

1. Never execute shell directly for Terraform — all runs go through the Terraform MCP.
2. Never generate AWS credentials — assume-role or ambient credentials only.
3. Never modify the Terraform state file.
4. Never bypass approval — `apply`, `destroy`, IAM changes, and network changes are gated.
5. Never let an agent perform another agent's job. Reviewers cannot modify or approve. Deployment cannot generate infrastructure.
6. Every action, state transition, and approval is written to an append-only audit trail.

## Implementation

1. Implement only the approved scope.
2. Follow the applicable toolkit specifications.
3. Treat each agent's `Cannot` list as a security boundary, not a suggestion.
4. Keep modules cohesive and interfaces explicit. Artifacts (`DeploymentPlan`, `TerraformProject`) are the contracts between stages.
5. Add automated tests for new behavior and relevant failure cases.
6. Do not introduce dependencies without explaining why they are needed.
7. Do not expose secrets or place credentials in source control.

## Validation

1. Run the relevant tests and static checks.
2. Report the exact commands executed and their results.
3. Identify untested behavior, limitations, and remaining risks.
4. Never claim a check passed unless it actually ran successfully.

## Reporting

Summarize the plan, implementation, files changed, validation evidence, and outstanding issues.

Do not claim that a toolkit workflow or specialized agent was invoked unless you can verify that it was actually loaded and used.
