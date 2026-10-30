# Project Engineering Instructions

## Project

Build **CloudPilot**, a Python application that turns natural-language requests into reviewed AWS infrastructure deployments, using the AI Engineering Toolkit specifications.

`specs/` and `.opencode/` are vendored from ai-engineering-toolkit. Treat them as read-only inputs: apply them, do not fork or weaken them.

## Toolchain

- **Python 3.12 is required** (`requires-python = ">=3.12"`). The system interpreter may be older — if `python3 --version` reports 3.10 or 3.11, do not use it; the editable install will refuse.
- **`uv` manages the interpreter and the environment.** If `uv` is absent: `python3 -m pip install --user uv`, then `export PATH="$HOME/.local/bin:$PATH"`.
- Set up and test:

  ```
  uv venv --python 3.12 .venv
  uv pip install -e . --group dev --python .venv/bin/python
  .venv/bin/python -m pytest -q
  ```

  The `--group dev` flag is required: it installs `[dependency-groups]` from `pyproject.toml`, which is where pytest is declared. Plain `uv pip install -e .` installs only `[project] dependencies` and leaves pytest absent.

- **Build backend:** hatchling.
- **Dependencies are deliberately unpinned.** Task 001 puts dependency pinning out of scope; it arrives with `tasks/002-dev-environment.md`. Do not commit a `uv.lock` yet, and do not add `==` pins to `[project] dependencies`.
- **Dev tooling is not configured yet.** `tasks/002-dev-environment.md` adds ruff, mypy, the Makefile and pre-commit. Until then the only gate is `.venv/bin/python -m pytest`.

## Before implementation

1. Inspect the repository and existing project conventions.
2. Read `specs/shared/workflow-principles.md` and `specs/workflows/build/workflow.md`.
3. Read the relevant domain and Python guidance.
4. Clarify ambiguous requirements before making significant design decisions.
5. Propose a plan with scope, design decisions, files to change, and acceptance criteria.

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
