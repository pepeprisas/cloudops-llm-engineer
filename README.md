# ai-cloudops-engineer

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

## Engineering baseline

This project is built using the [AI Engineering Toolkit](https://github.com/pepeprisas/ai-engineering-toolkit) specifications.

- `specs/` and `.opencode/agents/build/` are vendored from the toolkit, unmodified. See `specs/SOURCES.md` for provenance.
- `tasks/` holds the ordered implementation backlog.

Consult `AGENTS.md` before implementing.

## Status

Design stage. Specifications and the implementation roadmap are in place; no runtime code yet.
