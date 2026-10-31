"""Serving seam for the state machine: checkpointer, gate compile, gate ops.

Three responsibilities, all about making graph runs durable and gated:

- :func:`create_checkpointer` is the pluggable backend factory; ``Settings``
  selects the backend (in-memory, or SQLite for local development per Task
  012). Callers — the API layer (Task 010) and Phase 6 workflows — never
  construct a saver directly, so exactly one place decides where run state
  lives.
- :func:`create_gated_graph` is the **single serving compile site**: the
  graph every submit/status/approve/reject/cancel action runs against,
  compiled with a checkpointer and with ``GATE_INTERRUPT_BEFORE`` so a
  submitted run parks at the approval gate (status ==
  ``WAITING_FOR_APPROVAL``) instead of sliding past it. Compiling the
  graph anywhere else for serving would make "approval cannot be
  bypassed" true only for callers who remember the option; keeping the
  gate constant in :mod:`cloudpilot.graph.graph` and the compile here is
  what makes the property structural.
- :func:`start_run`, :func:`get_run`, :func:`record_decision` and
  :func:`approve_run` are the gate operations. They live in ``graph/``
  (not the API layer) because they encode transition policy: which
  states accept a decision, what the decision payload may contain, and
  that **approve is the only function that resumes the graph**. Tasks
  029-032 grow these into the full approval/reject/resume/cancel
  workflows with audit-trail integration (Task 033).

Checkpoints store the serialized ``DeploymentState`` and nothing else —
no AWS credentials, by construction: the state schema forbids
credential-shaped field names (``tests/test_state.py``) and no code path
puts secrets into state (``tests/test_checkpoints.py`` scans stored
bytes). The durable, append-only audit trail is a separate concern
(Task 033, ``core/audit.py``); this store is per-run trajectory.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.state import CompiledStateGraph

from cloudpilot.core.config import Settings
from cloudpilot.graph.graph import GATE_INTERRUPT_BEFORE, create_graph
from cloudpilot.graph.state import DeploymentState, DeploymentStatus, StateEvent

# Our custom types must be registered with the checkpoint serializer:
# langgraph's default is warn-but-allow and it announces that unregistered
# types "will be blocked in a future version" (blocked deserialization
# silently degrades StateEvent to raw dicts — verified). Registering keeps
# unpinned langgraph upgrades from breaking every stored run. New artifact
# models (Tasks 014/021/025-029) that tighten DeploymentState's slot types
# must add their (module, name) entries here.
_STATE_MSGPACK_ALLOWLIST = (
    ("cloudpilot.graph.state", "DeploymentStatus"),
    ("cloudpilot.graph.state", "StateEvent"),
)


def _create_serde() -> JsonPlusSerializer:
    """Serializer with CloudPilot's state types explicitly allowed."""
    return JsonPlusSerializer(allowed_msgpack_modules=_STATE_MSGPACK_ALLOWLIST)


def create_checkpointer(settings: Settings) -> BaseCheckpointSaver[Any]:
    """Return the checkpointer backend selected by ``settings``.

    - ``memory``: process-local, lost on restart — the honest default for
      tests and single-shot runs.
    - ``sqlite``: file-backed (Task 012), survives restarts, local-dev
      scale only. One connection per saver with ``check_same_thread=False``
      so FastAPI's threadpool may share it; SqliteSaver's own lock
      serializes writes. ``setup()`` runs eagerly here (idempotent
      ``CREATE TABLE IF NOT EXISTS``) so an unwritable path fails at
      startup instead of mid-workflow.
    """
    serde = _create_serde()
    if settings.checkpoint_backend == "memory":
        return InMemorySaver(serde=serde)
    connection = sqlite3.connect(settings.checkpoint_path, check_same_thread=False)
    saver = SqliteSaver(connection, serde=serde)
    saver.setup()
    return saver


def create_gated_graph(
    *, settings: Settings, checkpointer: BaseCheckpointSaver[Any] | None = None
) -> CompiledStateGraph[Any, Any, Any, Any]:
    """Compile the state machine for serving: durable and gate-paused.

    ``checkpointer`` may be passed explicitly (tests); otherwise the
    settings-selected backend is used. Either way the gate pause is
    meaningless without a checkpointer, so the combination is rejected
    rather than silently producing a graph that stops early with nothing
    saved (langgraph's behavior without a checkpointer).
    """
    if checkpointer is None:
        checkpointer = create_checkpointer(settings)
    return create_graph(checkpointer=checkpointer, interrupt_before=GATE_INTERRUPT_BEFORE)


def _as_config(thread_id: UUID | str) -> RunnableConfig:
    """LangGraph config with the thread_id in the expected shape."""
    return {"configurable": {"thread_id": str(thread_id)}}


def start_run(
    *,
    graph: CompiledStateGraph[Any, Any, Any, Any],
    request: str,
    deployment_id: UUID | str,
) -> dict[str, Any]:
    """Submit a new deployment request; the graph parks at the approval gate.

    Calls :meth:`~langgraph.graph.state.CompiledStateGraph.invoke` once.
    The graph was compiled with ``interrupt_before=[DEPLOYING]``, so a
    successful call always stops at ``status == WAITING_FOR_APPROVAL``
    with ``next == (DEPLOYING,)`` — a run that can only be advanced by
    :func:`approve_run`.

    Raises:
        ValueError: if ``request`` is empty.
    """
    if not request or not request.strip():
        raise ValueError("request cannot be empty")

    config = _as_config(deployment_id)
    return graph.invoke(DeploymentState(request=request.strip()).model_dump(), config)


def get_run(
    *, graph: CompiledStateGraph[Any, Any, Any, Any], deployment_id: UUID | str
) -> dict[str, Any]:
    """Return the latest checkpoint state for a deployment.

    Returns the full ``DeploymentState`` dict, including ``status``,
    ``deployment_id``, and keys needed to determine if the run is paused
    at the gate (`next` field via :meth:`~langgraph.graph.state.CompiledStateGraph.get_state`).
    """
    config = _as_config(deployment_id)
    snapshot = graph.get_state(config)
    return DeploymentState.model_validate(snapshot.values).model_dump()


def record_decision(
    *,
    graph: CompiledStateGraph[Any, Any, Any, Any],
    deployment_id: UUID | str,
    decision: str,
    reason: str | None = None,
) -> None:
    """Record a decision (reject or cancel) without resuming the run.

    This is the **only** way to advance a gated run away from
    ``WAITING_FOR_APPROVAL`` without approval (which is handled by
    :func:`approve_run`). It writes a terminal decision to the
    ``approval`` slot (``decision``, ``decided_at``, optional ``reason``)
    and leaves the run parked: the checkpoint's ``next`` still contains
    ``DEPLOYING``, so a subsequent ``invoke`` would simply resume to
    ``COMPLETED`` with no mutating action performed. This satisfies the
    Task 010 acceptance criterion that "reject/cancel act on the human-in-
    the-loop approval gate" — they record the decision and halt further
    progress.

    Precondition: the run must be parked at ``WAITING_FOR_APPROVAL`` and
    have no decision recorded yet (``approval is None``). The check
    happens server-side in this function so the API layer can return a
    409 conflict without leaking whether the run exists or its internal
    state.

    Raises:
        ValueError: if the run is not parked at the approval gate or
            already has a decision recorded.
    """
    config = _as_config(deployment_id)
    snapshot = graph.get_state(config)

    state = DeploymentState.model_validate(snapshot.values)
    if state.status is not DeploymentStatus.WAITING_FOR_APPROVAL:
        raise ValueError("decision can only be recorded at WAITING_FOR_APPROVAL")
    if state.approval is not None:
        raise ValueError("a decision has already been recorded")

    now = datetime.now(UTC)
    update: dict[str, Any] = {
        "status": state.status,
        "approval": {
            "decision": decision,
            "decided_at": now.isoformat(),
            **({"reason": reason} if reason else {}),
        },
        "events": [
            *state.events,
            StateEvent(status=state.status, message=f"recorded {decision} decision"),
        ],
        "updated_at": now,
    }

    graph.update_state(config, update, as_node="WAITING_FOR_APPROVAL")


def approve_run(
    *, graph: CompiledStateGraph[Any, Any, Any, Any], deployment_id: UUID | str
) -> dict[str, Any]:
    """Record approval and resume the run into DEPLOYING.

    This is the **only** function in the serving seam that advances a
    run past the approval gate. It performs three actions:

    1. Records the approval decision in the ``approval`` slot
       (``decision="approve"``, ``decided_at``, optional ``reason``).
    2. Updates ``status`` to ``DEPLOYING`` and logs the transition.
    3. Resumes the graph from the checkpoint with ``invoke(None, config)``.

    The result is a run that proceeds through the remaining nodes
    (VERIFYING, MONITORING, COMPLETED). A subsequent decision (reject/
    cancel) cannot be recorded because the state is no longer at
    ``WAITING_FOR_APPROVAL``.

    Raises:
        ValueError: if the run is not parked at the approval gate or
            has no approval recorded.
    """
    config = _as_config(deployment_id)
    snapshot = graph.get_state(config)

    state = DeploymentState.model_validate(snapshot.values)
    if state.status is not DeploymentStatus.WAITING_FOR_APPROVAL:
        raise ValueError("approval can only be recorded at WAITING_FOR_APPROVAL")
    if state.approval is None:
        raise ValueError("no decision recorded yet")

    now = datetime.now(UTC)
    # Build update with only the fields the state model expects.
    update: dict[str, Any] = {
        "approval": {**state.approval, **{"approved": True}},
        "status": DeploymentStatus.DEPLOYING,
        "updated_at": now,
        "events": [
            *state.events,
            StateEvent(
                status=DeploymentStatus.DEPLOYING,
                message="approval recorded; resuming to DEPLOYING",
            ),
        ],
    }

    graph.update_state(config, update, as_node="WAITING_FOR_APPROVAL")
    return graph.invoke(None, config)
