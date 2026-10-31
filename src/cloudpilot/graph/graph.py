"""LangGraph skeleton: one stub node per deployment status, linear edges.

Task 009 wires the state machine from :mod:`cloudpilot.graph.state`; every
node is a placeholder that only advances ``status`` and appends a
:class:`~cloudpilot.graph.state.StateEvent`. No agent, MCP, AWS, or shell
execution happens here — real node bodies replace the stubs in Tasks
015/020/025-028/034.

Invariants this module establishes for those later tasks:

- **Nodes are derived from ``DeploymentStatus``**: node name == status
  value, edges follow enum declaration order, so the graph cannot drift
  from the state machine. Phase 6 replaces the linear edge after
  ``WAITING_FOR_APPROVAL`` with conditional routing.
- **Delta updates only.** ``events`` uses an ``operator.add`` reducer; a
  node returns just its own new entries plus the fields it sets. Returning
  a pre-merged full list would append the whole log again.
- :func:`create_graph` is a pure factory — no settings, no singletons, no
  I/O at import or build time. Checkpointer wiring (Tasks 011/012) is
  passed in by the caller.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from cloudpilot.graph.state import DeploymentState, DeploymentStatus, StateEvent

# The exact StateGraph type that StateGraph(DeploymentState) infers; spelled
# out so add_node's overloads resolve against a concrete graph.
_Builder = StateGraph[DeploymentState, None, DeploymentState, DeploymentState]


def _add_stub_node(builder: _Builder, status: DeploymentStatus) -> None:
    """Register a placeholder node that advances to ``status`` and logs it.

    The node is defined and registered here (rather than returned from a
    factory function) because mypy cannot solve langgraph's ``NodeInputT``
    typevar from a callable whose type flows through a ``Callable`` alias —
    the inner ``def`` must reach ``add_node`` directly.
    """

    def node(state: DeploymentState) -> dict[str, Any]:
        return {
            "status": status,
            "updated_at": datetime.now(UTC),
            "events": [
                StateEvent(
                    status=status,
                    message=f"stub node for {status.value}: no work performed",
                )
            ],
        }

    builder.add_node(status.value, node)


def create_graph(
    *, checkpointer: BaseCheckpointSaver[Any] | None = None
) -> CompiledStateGraph[Any, Any, Any, Any]:
    """Build and compile the deployment state machine.

    One node per :class:`DeploymentStatus`, linear edges in declaration
    order from ``START`` to ``END``. ``checkpointer`` is the forward
    seam for Tasks 011/012; ``None`` means state lives only for the
    duration of ``invoke``.
    """
    builder = StateGraph(DeploymentState)
    statuses = list(DeploymentStatus)
    for status in statuses:
        _add_stub_node(builder, status)

    builder.add_edge(START, statuses[0].value)
    # Off-by-one windows: 11 statuses pair into 10 transitions by design.
    for previous, following in zip(statuses, statuses[1:], strict=False):
        builder.add_edge(previous.value, following.value)
    builder.add_edge(statuses[-1].value, END)

    # CompiledStateGraph's four type parameters are framework inference
    # details at this boundary; any-typed here deliberately (same stance as
    # the boto3 overrides in pyproject.toml), not because state is untyped.
    return builder.compile(checkpointer=checkpointer)
