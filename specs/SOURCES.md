# Specs Provenance

Records which files in this repository are vendored from the AI Engineering Toolkit and which are owned by this project.

**Source:** https://github.com/pepeprisas/ai-engineering-toolkit
**Pinned to commit:** `8ceeb06` (2026-10-11)

## Why this file exists

`specs/` and `.opencode/` are copied rather than git-submoduled, so this manifest is what keeps the two repositories reconcilable. It also records provenance while the toolkit's license is unresolved.

## Rules

- **Vendored-verbatim** files are read-only inputs. Apply them; do not fork or weaken them. The toolkit's own layering rule permits *additions* but forbids weakening: *"Domain specifications may add fields or stricter requirements, but they must not weaken this contract."*
- **Project-extension** files are owned here. They may extend the vendored contracts but must not weaken them.
- To upgrade, re-copy from the toolkit at a newer commit, then update the pinned commit above. Vendored files must remain byte-identical after re-copy.

## Vendored verbatim

| File | From |
|---|---|
| `specs/shared/workflow-principles.md` | `specs/shared/workflow-principles.md` |
| `specs/shared/finding-contract.md` | `specs/shared/finding-contract.md` |
| `specs/workflows/build/workflow.md` | `specs/workflows/build/workflow.md` |
| `specs/domains/architecture.md` | `specs/domains/architecture.md` |
| `specs/domains/ai-systems.md` | `specs/domains/ai-systems.md` |
| `specs/domains/security.md` | `specs/domains/security.md` |
| `specs/domains/data.md` | `specs/domains/data.md` |
| `specs/domains/reliability.md` | `specs/domains/reliability.md` |
| `specs/languages/python.md` | `specs/languages/python.md` |
| `.opencode/agents/build/supervisor.md` | `.opencode/agents/build/supervisor.md` |
| `.opencode/agents/build/architecture-advisor.md` | `.opencode/agents/build/architecture-advisor.md` |
| `.opencode/agents/build/ai-systems-advisor.md` | `.opencode/agents/build/ai-systems-advisor.md` |
| `.opencode/agents/build/security-advisor.md` | `.opencode/agents/build/security-advisor.md` |
| `.opencode/agents/build/data-advisor.md` | `.opencode/agents/build/data-advisor.md` |
| `.opencode/agents/build/reliability-advisor.md` | `.opencode/agents/build/reliability-advisor.md` |
| `.opencode/agents/build/python-advisor.md` | `.opencode/agents/build/python-advisor.md` |

Verification: `diff -rq <toolkit>/specs specs` and `diff -rq <toolkit>/.opencode .opencode` must report no differences.

## Project extension

| File | Notes |
|---|---|
| `specs/domains/cloud-infrastructure.md` | *Planned.* IaC and cloud guidance the toolkit does not cover: ingress exposure, public data stores, IAM wildcards, encryption at rest, provider pinning, state-file safety, drift. |
| `specs/domains/finops.md` | *Planned.* Cost-estimation criteria for the COST_REVIEW stage. |

These are the only files permitted to live alongside vendored specs without a toolkit counterpart. Everything else in `specs/` must be verbatim.

## Project-owned

| File | Notes |
|---|---|
| `AGENTS.md` | Project engineering instructions. |
| `README.md` | Product overview. |
| `specs/SOURCES.md` | This manifest. |
