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

Agent roster: Planner · Terraform · Security · Cost · Best Practices · Documentation · Deployment · Report.

## Engineering baseline

This project is built using the [AI Engineering Toolkit](https://github.com/pepeprisas/ai-engineering-toolkit) specifications.

- `specs/` and `.opencode/agents/build/` are vendored from the toolkit, unmodified. See `specs/SOURCES.md` for provenance.
- `docs/` holds CloudPilot-specific design (architecture, state machine, agents, MCP, API).
- `tasks/` holds the ordered implementation backlog.

Consult `AGENTS.md` before implementing.

## Status

Design stage. Specifications and backlog are in place; no runtime code yet.
