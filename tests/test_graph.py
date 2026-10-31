"""Unit tests for the graph skeleton: structure and placeholder end-to-end run."""

from __future__ import annotations

from typing import Any

import pytest
from langgraph.graph import END, START

from cloudpilot.graph.graph import create_graph
from cloudpilot.graph.state import DeploymentState, DeploymentStatus


@pytest.mark.unit
def test_graph_compiles() -> None:
    assert create_graph() is not None


@pytest.mark.unit
def test_one_node_per_status_plus_terminals() -> None:
    names = set(create_graph().get_graph().nodes)  # nodes is a name-keyed dict
    assert names - {START, END} == {status.value for status in DeploymentStatus}


@pytest.mark.unit
def test_end_to_end_placeholder_run_reaches_completed() -> None:
    initial = DeploymentState(request="deploy a private S3 bucket")
    final: dict[str, Any] = create_graph().invoke(initial.model_dump())

    assert final["status"] is DeploymentStatus.COMPLETED
    # Exactly one appended event per node proves the operator.add reducer
    # accumulates instead of replacing — and that no event is duplicated.
    assert [event.status for event in final["events"]] == list(DeploymentStatus)
    # Identity and creation time survive the run: if unwritten channels were
    # left to re-apply their default factories at every node, these would
    # have drifted.
    assert final["deployment_id"] == initial.deployment_id
    assert final["created_at"] == initial.created_at
    assert final["updated_at"] >= initial.updated_at
