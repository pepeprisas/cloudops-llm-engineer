"""Checkpointer seam and the serving compile of the state machine.

Two responsibilities, both about making graph runs durable:

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

Checkpoints store the serialized ``DeploymentState`` and nothing else —
no AWS credentials, by construction: the state schema forbids
credential-shaped field names (``tests/test_state.py``) and no code path
puts secrets into state (``tests/test_persistence.py`` scans stored
checkpoint keys). The durable, append-only audit trail is a separate
concern (Task 033, ``core/audit.py``); this store is per-run trajectory.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.state import CompiledStateGraph

from cloudpilot.core.config import Settings
from cloudpilot.graph.graph import GATE_INTERRUPT_BEFORE, create_graph

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
