"""FastAPI routes wired to the LangGraph gate operations.

The API exposes:

- ``POST /deployments`` — submit a deployment request; the run parks at
  the approval gate.
- ``GET /deployments/{id}`` — get the current status and key state.
- ``POST /deployments/{id}/approve`` — record approval and resume the run
  into the mutating phase (``DEPLOYING``).
- ``POST /deployments/{id}/reject`` and ``/cancel`` — record a terminal
  decision and park the run (no further progress).

All routes log every action with ``deployment_id`` and route metadata via
``core/logging.set_log_context``. The approval gate is enforced by the
graph compile (``interrupt_before=[DEPLOYING]``): only ``/approve`` calls
``graph.invoke(None, ...)`` to resume; reject/cancel merely write the
decision to state via ``graph.update_state`` without resuming.

AuthN/AuthZ and rate limiting are explicitly out of scope for Task 010;
they are future work. For now, the ``deployment_id`` serves as an opaque
capability handle (v4 UUID, 128-bit entropy) — see Known Limitations.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from cloudpilot.core.config import Settings
from cloudpilot.core.logging import set_log_context
from cloudpilot.graph.persistence import (
    approve_run,
    create_gated_graph,
    get_run,
    record_decision,
    start_run,
)
from cloudpilot.graph.state import DeploymentState

router = APIRouter()


@router.post("/deployments")
def create_deployment(request: dict[str, str]) -> dict[str, Any]:
    """Submit a deployment request; the run parks at the approval gate.

    Raises:
        HTTPException 422: if the request body is invalid.
        HTTPException 500: on internal error.
    """
    if not request.get("request") or not request["request"].strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="request cannot be empty",
        )
    if len(request["request"]) > 10_000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="request exceeds maximum length",
        )

    settings = Settings(_env_file=None)
    graph = create_gated_graph(settings=settings)
    deployment_id = uuid4()
    set_log_context(deployment_id=str(deployment_id), route="create_deployment")
    try:
        result = start_run(
            graph=graph, request=request["request"].strip(), deployment_id=deployment_id
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to start deployment",
        ) from exc

    state = DeploymentState.model_validate(result)
    set_log_context(
        deployment_id=str(deployment_id), status=state.status.value, route="create_deployment"
    )
    return {
        "deployment_id": state.deployment_id,
        "status": state.status,
        "created_at": state.created_at,
        "updated_at": state.updated_at,
    }


@router.get("/deployments/{deployment_id}")
def get_deployment(deployment_id: UUID) -> dict[str, Any]:
    """Return the current status and key state for a deployment.

    Raises:
        HTTPException 404: if the deployment does not exist.
    """
    settings = Settings(_env_file=None)
    graph = create_gated_graph(settings=settings)
    set_log_context(deployment_id=str(deployment_id), route="get_deployment")
    try:
        result = get_run(graph=graph, deployment_id=deployment_id)
        state = DeploymentState.model_validate(result)
        set_log_context(
            deployment_id=str(deployment_id), status=state.status.value, route="get_deployment"
        )
        return {
            "deployment_id": state.deployment_id,
            "status": state.status,
            "created_at": state.created_at,
            "updated_at": state.updated_at,
            "approval": state.approval,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="deployment not found",
        ) from exc


@router.post("/deployments/{deployment_id}/approve")
def approve_deployment(deployment_id: UUID) -> dict[str, Any]:
    """Record approval and resume the run into the mutating phase.

    Raises:
        HTTPException 404: if the deployment does not exist.
        HTTPException 409: if the run is not at the approval gate or a
            decision has already been recorded.
    """
    settings = Settings(_env_file=None)
    graph = create_gated_graph(settings=settings)
    set_log_context(deployment_id=str(deployment_id), route="approve_deployment")
    try:
        result = approve_run(graph=graph, deployment_id=deployment_id)
        state = DeploymentState.model_validate(result)
        set_log_context(
            deployment_id=str(deployment_id), status=state.status.value, route="approve_deployment"
        )
        return {
            "deployment_id": state.deployment_id,
            "status": state.status,
            "created_at": state.created_at,
            "updated_at": state.updated_at,
        }
    except ValueError as exc:
        if "not parked" in str(exc) or "no decision recorded" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="deployment not found",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to approve deployment",
        ) from exc


@router.post("/deployments/{deployment_id}/reject")
def reject_deployment(deployment_id: UUID, body: dict[str, str] | None = None) -> dict[str, Any]:
    """Record a rejection decision and halt the run.

    Raises:
        HTTPException 404: if the deployment does not exist.
        HTTPException 409: if the run is not at the approval gate or a
            decision has already been recorded.
    """
    return _record_decision_impl(
        deployment_id=deployment_id,
        decision="reject",
        reason=(body or {}).get("reason"),
    )


@router.post("/deployments/{deployment_id}/cancel")
def cancel_deployment(deployment_id: UUID, body: dict[str, str] | None = None) -> dict[str, Any]:
    """Record a cancellation decision and halt the run.

    Raises:
        HTTPException 404: if the deployment does not exist.
        HTTPException 409: if the run is not at the approval gate or a
            decision has already been recorded.
    """
    return _record_decision_impl(
        deployment_id=deployment_id,
        decision="cancel",
        reason=(body or {}).get("reason"),
    )


def _record_decision_impl(
    *, deployment_id: UUID, decision: str, reason: str | None = None
) -> dict[str, Any]:
    settings = Settings(_env_file=None)
    graph = create_gated_graph(settings=settings)
    set_log_context(deployment_id=str(deployment_id), route=f"record_{decision}")
    try:
        record_decision(graph=graph, deployment_id=deployment_id, decision=decision, reason=reason)
        state = DeploymentState.model_validate(get_run(graph=graph, deployment_id=deployment_id))
        set_log_context(
            deployment_id=str(deployment_id), status=state.status.value, route=f"record_{decision}"
        )
        return {
            "deployment_id": state.deployment_id,
            "status": state.status,
            "created_at": state.created_at,
            "updated_at": state.updated_at,
            "approval": state.approval,
        }
    except ValueError as exc:
        if "not parked" in str(exc) or "already" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="deployment not found",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to record {decision}",
        ) from exc
