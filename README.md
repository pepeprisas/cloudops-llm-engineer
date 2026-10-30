# cloudops-llm-engineer

**CloudPilot** — an AI agent that turns natural-language requests ("Deploy a FastAPI application") into safe, reviewed AWS infrastructure deployments.

Target users: solo developers, startups, and platform engineers.

## What it does

A request advances through a gated state machine. Nothing mutates AWS until a human approves:

```
REQUEST_RECEIVED → PLANNING → GENERATING_TERRAFORM → VALIDATING →
SECURITY_REVIEW → COST_REVIEW → WAITING_FOR_APPROVAL → DEPLOYING →
VERIFYING → MONITORING → COMPLETED
```

## Core values

- **Human approval** before anything is applied.
- **Cost awareness** — estimated monthly cost before approval, not after.
- **Security review** built into the pipeline rather than bolted on.
- **Capability separation** — each agent has a hard `Cannot` list. Limiting capability limits blast radius.
- **Append-only audit trail** covering every action, state transition, and approval.

## Architecture

```
Client → FastAPI → LangGraph state machine → Agents → MCP servers → AWS
```

Agents reach external systems only through MCP servers, never directly:

- `terraform` — init, validate, fmt, plan, apply, destroy (`apply`/`destroy` are approval-gated)
- `cloudwatch` — logs, metrics, alarms, health (read-only)
- `github` — create PR/issue, commit, comment, review

## Agent boundaries

Each agent has a hard capability boundary. Limiting capability limits blast radius.

| Agent | Cannot |
|---|---|
| Planner | Deploy infrastructure · Generate Terraform |
| Terraform | Apply infrastructure · Run terraform plan · Execute shell directly |
| Security | Modify Terraform · Deploy infrastructure · Approve |
| Cost | Modify Terraform · Deploy infrastructure · Approve |
| Best Practices | Modify Terraform · Deploy infrastructure · Approve |
| Documentation | Modify Terraform · Deploy infrastructure |
| Deployment | Generate infrastructure · Generate Terraform · Bypass approval · Execute shell directly |
| Report | Modify infrastructure · Approve |

## Layout

```
src/cloudpilot/
├── agents/    planner, terraform, security, cost, best-practices,
│              documentation, deployment, report
├── graph/     LangGraph state machine and its nodes
├── mcp/       external-provider boundary: terraform, cloudwatch, github
├── api/       FastAPI transport
├── models/    artifact contracts (DeploymentPlan, TerraformProject)
└── core/      cross-cutting policy: config, logging, AWS session, audit,
│              retry, llm
tests/
```

### Import direction

Dependencies flow one way. Nothing may invert these:

| Package | May import | Must not import |
|---|---|---|
| `models/` | nothing from `cloudpilot` | everything else |
| `core/` | `models/` | `graph/`, `agents/`, `mcp/`, `api/` |
| `mcp/` | `core/`, `models/` | `agents/`, `graph/`, `api/` |
| `agents/` | `core/`, `models/`, `mcp/` | `graph/`, `api/` |
| `graph/` | `agents/`, `mcp/`, `core/`, `models/` | `api/` |
| `api/` | `graph/`, `models/`, `core/` | — nothing imports it |

Three consequences worth stating explicitly:

- **`models/` is a leaf.** The artifact contracts are the interface between stages, so they must not depend on the agents that produce them or the graph that carries them. Otherwise every consumer couples to a producer.
- **`api/` is transport only.** Approval decisions, retries, and orchestration stay in `graph/`. Nothing imports `api/`.
- **`mcp/` is the boundary to external systems.** Nothing outside it talks to AWS, GitHub, or terraform directly — which is what makes the "never execute shell directly" rule enforceable rather than aspirational.

These rules are **enforced** by `tests/test_import_direction.py`, an AST check in the pytest suite (added by Task 002). Change the allow-table there together with this table.

## Engineering baseline

This project is built using the [AI Engineering Toolkit](https://github.com/pepeprisas/ai-engineering-toolkit) specifications.

- `specs/` and `.opencode/agents/build/` are vendored from the toolkit, unmodified. See `specs/SOURCES.md` for provenance.
- `tasks/` holds the ordered implementation backlog.

Consult `AGENTS.md` before implementing.

## Status

Design stage. Specifications and the implementation roadmap are in place; no runtime code yet.
