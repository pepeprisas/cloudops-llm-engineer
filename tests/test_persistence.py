"""Unit tests for the checkpointer seam and the gate-paused serving graph.

Task 011's contract: a run can be interrupted at the approval gate and
resumed from its last checkpoint, the backend is pluggable, and
checkpoints never carry credential-shaped data. The pause/resume
semantics pinned here are the ones Task 010's API layer will build on
(approve == resume; reject/cancel == recorded decision, no resume).
"""

from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

import pytest
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import Checkpoint
from langgraph.checkpoint.memory import InMemorySaver

from cloudpilot.graph.graph import GATE_INTERRUPT_BEFORE, create_graph
from cloudpilot.graph.persistence import create_checkpointer, create_gated_graph
from cloudpilot.graph.state import DeploymentState, DeploymentStatus

# Mirror of tests/test_state.py: no credential-shaped key may appear in
# what a checkpoint actually stores (Task 011 acceptance criterion).
CREDENTIAL_FIELD_DENYLIST = re.compile(
    r"access_key|secret|password|token|credential", re.IGNORECASE
)


def _thread_config() -> RunnableConfig:
    return {"configurable": {"thread_id": str(uuid4())}}


def _park_at_gate(graph: Any) -> RunnableConfig:
    """Run a fresh deployment up to the approval gate; return its config."""
    config = _thread_config()
    graph.invoke(DeploymentState(request="deploy a private S3 bucket").model_dump(), config)
    return config


def _state_from_checkpoint(checkpoint: Checkpoint) -> DeploymentState:
    """Validate a checkpoint's channels, ignoring langgraph's own bookkeeping.

    ``channel_values`` also carries framework-internal channels (e.g.
    ``branch:to:DEPLOYING``); ``extra="forbid"`` correctly rejects them, so
    the state contract is validated over our fields only.
    """
    channels = checkpoint["channel_values"]
    return DeploymentState.model_validate(
        {key: value for key, value in channels.items() if key in DeploymentState.model_fields}
    )


@pytest.mark.unit
def test_run_parks_at_the_approval_gate() -> None:
    graph = create_gated_graph()
    config = _thread_config()

    paused = graph.invoke(DeploymentState(request="resize the cluster").model_dump(), config)

    # Status is WAITING_FOR_APPROVAL because the gate node ran; `next`
    # names the node the breakpoint holds back — the first mutating node.
    assert paused["status"] is DeploymentStatus.WAITING_FOR_APPROVAL
    snapshot = graph.get_state(config)
    assert snapshot.next == (DeploymentStatus.DEPLOYING.value,)


@pytest.mark.unit
def test_resumed_run_completes_with_exactly_one_event_per_node() -> None:
    graph = create_gated_graph()
    config = _park_at_gate(graph)

    final = graph.invoke(None, config)  # input None == resume from checkpoint

    assert final["status"] is DeploymentStatus.COMPLETED
    # One appended event per node, in machine order: the reducer
    # accumulated across the pause/resume boundary without dropping or
    # duplicating entries.
    assert [event.status for event in final["events"]] == list(DeploymentStatus)


@pytest.mark.unit
def test_interrupts_require_a_checkpointer() -> None:
    # Without a checkpointer langgraph stops the run silently with nothing
    # persisted and no error — the factory must reject that combination.
    with pytest.raises(ValueError, match="checkpointer"):
        create_graph(interrupt_before=GATE_INTERRUPT_BEFORE)


@pytest.mark.unit
def test_gated_graph_defaults_to_the_seam_backend() -> None:
    # The serving compile must work with the factory default (in-memory
    # checkpointer) so no caller needs to wire a saver to get the gate.
    graph = create_gated_graph()
    config = _thread_config()
    graph.invoke(DeploymentState(request="spin up a private VPC").model_dump(), config)
    assert graph.get_state(config).next == (DeploymentStatus.DEPLOYING.value,)


@pytest.mark.unit
def test_threads_are_isolated() -> None:
    graph = create_gated_graph()
    _park_at_gate(graph)

    unknown = graph.get_state(_thread_config())

    assert unknown.next == ()
    assert unknown.values.get("deployment_id") is None


@pytest.mark.unit
def test_checkpoint_round_trip_preserves_the_state_contract() -> None:
    checkpointer = create_checkpointer()
    graph = create_gated_graph(checkpointer=checkpointer)
    config = _park_at_gate(graph)

    stored = checkpointer.get_tuple(config)
    assert stored is not None
    reloaded = _state_from_checkpoint(stored.checkpoint)

    original = DeploymentState.model_validate(graph.get_state(config).values)
    assert reloaded.deployment_id == original.deployment_id
    assert reloaded.created_at == original.created_at
    assert reloaded.status is DeploymentStatus.WAITING_FOR_APPROVAL
    # Every node up to and including the gate has logged; the nodes after
    # it (held back by the breakpoint) have not.
    statuses = list(DeploymentStatus)
    ran = statuses[: statuses.index(DeploymentStatus.WAITING_FOR_APPROVAL) + 1]
    assert [event.status for event in reloaded.events] == ran


@pytest.mark.unit
def test_no_credential_shaped_keys_are_stored() -> None:
    checkpointer = create_checkpointer()
    graph = create_gated_graph(checkpointer=checkpointer)
    config = _park_at_gate(graph)

    stored = checkpointer.get_tuple(config)
    assert stored is not None
    keys = list(stored.checkpoint["channel_values"])

    assert [key for key in keys if CREDENTIAL_FIELD_DENYLIST.search(key)] == []


@pytest.mark.unit
def test_in_memory_is_the_pluggable_default() -> None:
    assert isinstance(create_checkpointer(), InMemorySaver)
