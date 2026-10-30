# 000 — Master Task List

Implementation roadmap for CloudPilot. Tasks are grouped into phases that build
thin vertical slices: foundation first, then the workflow engine, then one
intelligent component at a time. Each numbered task has its own file
(`NNN-slug.md`) with Goal / Inputs / Outputs / Dependencies / Acceptance
Criteria / Out of Scope / Deliverables.

Source code lives under the `src/cloudpilot/` package; tests under `tests/`.

## Progress

Status is tracked on the phase lists below. `[x]` means complete **and validated** —
not merely written. If validation is blocked, the task stays `[ ]` and the blockage
is recorded in the commit message. Git history carries the rationale for each change.

Count the remaining work with:

```
grep -c '^- \[ \]' tasks/000-tasks-list.md
```

## Dependency rules (must hold)

- Terraform `init/validate/fmt/plan/apply/destroy` run **only** through the
  Terraform MCP (019) — never via direct shell.
- `apply` and `destroy` are **approval-gated** (Phase 6 must exist before Phase 7
  mutates anything).
- The `DeploymentPlan` schema (014) is a hard dependency of every Phase 3/4 task.
- No agent calls a model client directly — all model access goes through the LLM agent abstraction (049).
- Every action that changes state or AWS resources writes to the audit trail (033).

## Phase 1 — Foundation (no AI yet)

- [x] 001 Project scaffold
- [x] 002 Development environment
- [x] 003 Logging
- [x] 004 Configuration management
- [x] 005 Testing framework
- [ ] 006 Docker
- [x] 007 AWS authentication & credentials  *(assume-role/session, never generate creds)*

## Phase 2 — Core Workflow (workflow engine)

- [ ] 008 Deployment state model
- [ ] 009 LangGraph skeleton
- [ ] 010 API layer (FastAPI)  *(the `User → FastAPI → LangGraph` entry point)*
- [ ] 011 Graph persistence
- [ ] 012 Checkpoint storage
- [ ] 013 Graph visualization

## Phase 3 — Planner (first intelligent component)

- [ ] 014 DeploymentPlan schema  *(front of phase — it is the contract)*
- [ ] 049 LLM Agent Abstraction  *(added later, numbered 049 — scheduled here because 015 and 020 both depend on it)*
- [ ] 015 Planner Agent
- [ ] 016 Planner prompt
- [ ] 017 Requirement extraction
- [ ] 018 Clarification questions

## Phase 4 — Terraform

- [ ] 019 Terraform MCP server  *(validate/fmt/plan need it)*
- [ ] 020 Terraform Agent
- [ ] 021 Terraform templates
- [ ] 022 Terraform validation
- [ ] 023 Terraform formatting
- [ ] 024 Terraform plan

## Phase 5 — Reviews

- [ ] 025 Security Agent
- [ ] 026 Cost Agent
- [ ] 027 Best Practices Agent
- [ ] 028 Documentation Agent

## Phase 6 — Human Governance

- [ ] 029 Approval workflow
- [ ] 030 Reject workflow
- [ ] 031 Resume workflow
- [ ] 032 Cancel workflow
- [ ] 033 Audit trail  *(append-only log of every action & approval)*

## Phase 7 — Deployment

- [ ] 034 Deployment Agent  *(orchestrates apply via MCP; cannot generate infra)*
- [ ] 035 Apply workflow
- [ ] 036 Rollback workflow
- [ ] 037 State recovery
- [ ] 038 Drift detection

## Phase 8 — Monitoring

- [ ] 039 CloudWatch MCP
- [ ] 040 Health checks (Verify)
- [ ] 041 Incident detection
- [ ] 042 Automatic retries
- [ ] 043 Deployment report

## Phase 9 — GitHub

- [ ] 044 GitHub MCP
- [ ] 045 Commit generated Terraform
- [ ] 046 Create PR
- [ ] 047 Review comments
- [ ] 048 Merge workflow
