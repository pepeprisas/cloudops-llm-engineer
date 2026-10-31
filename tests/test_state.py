"""Unit tests for the deployment state model: contract, defaults, round-trip.

These lock the checkpoint-serializable contract before any graph node
exists: the exact status machine, fresh-state defaults, lossless JSON
round-trip, and schema guards (frozen, extra="forbid", no
credential-shaped field names).
"""

from __future__ import annotations

import re
from uuid import UUID

import pytest
from pydantic import ValidationError

from cloudpilot.graph.state import (
    STATE_SCHEMA_VERSION,
    DeploymentState,
    DeploymentStatus,
    StateEvent,
)

# Mirror of tests/test_config.py's denylist: no credential-shaped field
# names may enter the state, because checkpoints are persisted verbatim and
# the log-stream redaction in core/logging.py does not cover them.
CREDENTIAL_FIELD_DENYLIST = re.compile(
    r"access_key|secret|password|token|credential", re.IGNORECASE
)

# The exact machine from tasks/008-state-model.md and docs/architecture.md.
EXPECTED_STATES = (
    "REQUEST_RECEIVED",
    "PLANNING",
    "GENERATING_TERRAFORM",
    "VALIDATING",
    "SECURITY_REVIEW",
    "COST_REVIEW",
    "WAITING_FOR_APPROVAL",
    "DEPLOYING",
    "VERIFYING",
    "MONITORING",
    "COMPLETED",
)


@pytest.mark.unit
def test_status_enum_is_complete_and_ordered() -> None:
    # Order matters: Task 009 generates nodes and edges by iterating the
    # enum, so a reorder silently reorders the state machine.
    assert tuple(status.value for status in DeploymentStatus) == EXPECTED_STATES


@pytest.mark.unit
def test_fresh_state_needs_only_a_request() -> None:
    state = DeploymentState(request="spin up a private VPC")
    assert state.status is DeploymentStatus.REQUEST_RECEIVED
    assert isinstance(state.deployment_id, UUID)
    assert state.events == []
    assert state.plan is None
    assert state.terraform is None
    assert state.reviews is None
    assert state.approval is None
    # Timezone-aware: naive timestamps would break equality against UTC
    # values written by other code paths.
    assert state.created_at.tzinfo is not None
    assert state.updated_at.tzinfo is not None


@pytest.mark.unit
def test_empty_request_is_rejected() -> None:
    with pytest.raises(ValidationError):
        DeploymentState(request="")


@pytest.mark.unit
def test_json_round_trip_is_lossless() -> None:
    populated = DeploymentState(
        request="deploy a private S3 bucket",
        status=DeploymentStatus.SECURITY_REVIEW,
        plan={"resources": ["s3_bucket.private"]},
        terraform={"files": {"main.tf": "# placeholder"}},
        reviews={"security": {"findings": []}},
        approval={"decision": "pending"},
        events=[
            StateEvent(status=DeploymentStatus.REQUEST_RECEIVED, message="received"),
            StateEvent(status=DeploymentStatus.PLANNING, message="planning started"),
        ],
    )
    for state in (DeploymentState(request="fresh"), populated):
        assert DeploymentState.model_validate_json(state.model_dump_json()) == state


@pytest.mark.unit
def test_round_trip_preserves_enum_member_identity() -> None:
    # Guards against a future use_enum_values=True, which would silently
    # turn status into a bare str in graph nodes.
    state = DeploymentState(request="resize the cluster", status=DeploymentStatus.COST_REVIEW)
    reloaded = DeploymentState.model_validate_json(state.model_dump_json())
    assert reloaded.status is DeploymentStatus.COST_REVIEW
    assert reloaded.events == []


@pytest.mark.unit
def test_schema_version_defaults_to_current() -> None:
    assert DeploymentState(request="x").schema_version == STATE_SCHEMA_VERSION
    assert STATE_SCHEMA_VERSION == 1


@pytest.mark.unit
def test_state_is_immutable() -> None:
    # Frozen: nodes may not mutate state outside LangGraph's update protocol.
    state = DeploymentState(request="x")
    with pytest.raises(ValidationError):
        # ``type: ignore[misc]``: mypy enforces this statically (read-only
        # property); the test proves pydantic enforces it at runtime too.
        state.status = DeploymentStatus.PLANNING  # type: ignore[misc]


@pytest.mark.unit
def test_model_copy_is_the_sanctioned_update_path() -> None:
    state = DeploymentState(request="x")
    event = StateEvent(status=DeploymentStatus.PLANNING, message="moved on")
    updated = state.model_copy(
        update={"status": DeploymentStatus.PLANNING, "events": [*state.events, event]}
    )
    assert updated.status is DeploymentStatus.PLANNING
    assert updated.events == [event]
    assert state.status is DeploymentStatus.REQUEST_RECEIVED  # original untouched


@pytest.mark.unit
def test_unknown_fields_are_rejected() -> None:
    # A checkpoint containing a field this version does not know fails
    # loudly instead of being silently truncated.
    payload = DeploymentState(request="x").model_dump(mode="json") | {"surprise": True}
    with pytest.raises(ValidationError):
        DeploymentState.model_validate(payload)


@pytest.mark.unit
def test_no_field_name_looks_like_a_credential() -> None:
    # Guards the "checkpoints never store AWS credentials" invariant at the
    # schema level (Tasks 011/012 acceptance criteria).
    offenders = [
        name for name in DeploymentState.model_fields if CREDENTIAL_FIELD_DENYLIST.search(name)
    ]
    assert offenders == []
