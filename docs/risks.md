# Risks and Limitations

This document tracks risks and limitations across all phases of CloudPilot.

## Phase 1 — Foundation

| Task | Risk/Limitation | Status |
|---|---|---|
| 002 | No dependency pinning until Task 002 follow-up | Open - blocked by Task 002 |
| 003 | Logs are mutable and rotatable; not suitable as audit trail | Open - replaced by Task 033 |
| 004 | AWS credentials must never appear in env/.env/compose; only ambient/STS | Continuous - enforced by design |
| 007 | Ambient credentials required for live tests; tests may fail without them | Open - tests run offline as fallback |

## Phase 2 — Core Workflow

| Task | Risk/Limitation | Status |
|---|---|---|
| 010 | AuthN/AuthZ not implemented; `deployment_id` serves as capability handle | Open - addressed in follow-up |
| 010 | Rate limiting not implemented | Open - addressed in follow-up |
| 011 | Unpinned langgraph; future upgrades require verifying API surface | Open - addressed in follow-up |
| 012 | SQLite concurrency: one connection with internal lock; local-dev only | Open - production backend pending |
| 012 | No audit trail; structured logs used instead | Open - replaced by Task 033 |
| 013 | PNG rendering requires pygraphviz (optional dep) | Open - graceful fallback if absent |

## Phase 3+ — Planned

Phase 3-9 risks are captured in their respective task definitions and will be added
to this table when implemented.

## Risk Resolution

Risks are resolved when:
1. The blocking task is completed
2. A workaround is documented
3. Risk acceptance is documented with rationale

Each risk entry includes a status (`Open`, `Mitigated`, `Accepted`) and links to
related tasks or documentation.
