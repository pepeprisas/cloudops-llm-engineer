"""Deployment workflow state: the contract threaded through every graph node.

:class:`DeploymentState` is the single data structure the LangGraph nodes
(Task 009) read and receive as updates, and the shape Tasks 011/012 will
persist in checkpoints. Three boundaries this module sets:

- **Field names are the checkpoint contract.** Once checkpoints exist,
  renaming a field invalidates stored runs; treat names as append-only.
  Field *types* legitimately tighten later: the artifact slots (``plan``,
  ``terraform``, ``reviews``, ``approval``) are ``dict[str, Any] | None``
  placeholders until their real models land (Tasks 014, 021, 025-029), and
  pydantic coerces previously stored dicts when the annotations change.
  No placeholder artifact models are invented in ``models/`` ahead of those
  tasks — that is their contract to define, not this module's.
- **``events`` is not the audit trail.** It is the per-run trajectory
  embedded in graph state, checkpointed with the run. Task 033's
  append-only store in ``core/audit.py`` is the durable system of record;
  nodes will eventually write to both. Event entries stay metadata-sized
  (status + message) — never artifact payloads, prompts, or credentials.
- **Immutable state, delta updates.** The model is frozen so a node cannot
  mutate state outside LangGraph's update protocol; nodes return partial
  updates that the graph merges. ``events`` carries an ``operator.add``
  reducer, so nodes must return only their *own* new entries — returning a
  pre-merged list would append the whole log again.
"""

from __future__ import annotations

import operator
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

# Bump when the serialized shape of DeploymentState changes incompatibly;
# checkpoint load and state recovery (Tasks 012/037) branch on this instead
# of sniffing fields. Migration logic belongs to those tasks, not here.
STATE_SCHEMA_VERSION = 1


class DeploymentStatus(StrEnum):
    """The gated deployment state machine, in transition order.

    Declaration order *is* the machine from ``docs/architecture.md``: Task
    009 generates graph nodes and linear edges by iterating this enum, so
    reordering members reorders the graph. ``WAITING_FOR_APPROVAL`` gains
    reject/cancel branches in Phase 6; ``COMPLETED`` is terminal. Values are
    identical to names so the wire format and node names are stable.
    """

    REQUEST_RECEIVED = "REQUEST_RECEIVED"
    PLANNING = "PLANNING"
    GENERATING_TERRAFORM = "GENERATING_TERRAFORM"
    VALIDATING = "VALIDATING"
    SECURITY_REVIEW = "SECURITY_REVIEW"
    COST_REVIEW = "COST_REVIEW"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    DEPLOYING = "DEPLOYING"
    VERIFYING = "VERIFYING"
    MONITORING = "MONITORING"
    COMPLETED = "COMPLETED"


def _utcnow() -> datetime:
    """Timezone-aware now; naive timestamps would break round-trip equality."""
    return datetime.now(UTC)


class StateEvent(BaseModel):
    """One entry in the per-run event log (see module docstring on scope)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    at: datetime = Field(default_factory=_utcnow)
    status: DeploymentStatus
    message: str = Field(min_length=1)


class DeploymentState(BaseModel):
    """Full state of one deployment run, from request to completion.

    Construct from the request alone — ``DeploymentState(request=...)`` —
    for a fresh run: everything else defaults. The artifact slots are
    ``None`` until the tasks that own them fill them in; their keys are
    documented in the module docstring.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: int = STATE_SCHEMA_VERSION
    deployment_id: UUID = Field(default_factory=uuid4)
    request: str = Field(min_length=1)
    status: DeploymentStatus = DeploymentStatus.REQUEST_RECEIVED

    # Artifact slots. Names are the stable contract; types tighten when the
    # owning task lands. `reviews` is keyed by reviewer name ("security",
    # "cost", "best_practices", "documentation") because four review agents
    # (Tasks 025-028) feed two review states in the machine.
    plan: dict[str, Any] | None = None  # DeploymentPlan, Task 014
    terraform: dict[str, Any] | None = None  # TerraformProject, Task 021
    reviews: dict[str, Any] | None = None  # Tasks 025-028
    approval: dict[str, Any] | None = None  # decision, Task 029

    # Per-run trajectory (not the Task 033 audit trail). The reducer appends
    # node updates instead of replacing the list; see module docstring.
    events: Annotated[list[StateEvent], operator.add] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
