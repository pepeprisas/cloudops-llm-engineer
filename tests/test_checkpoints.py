"""Unit tests for the SQLite checkpointer backend (Task 012).

Contract: the settings-driven factory returns the right backend, schema
setup is idempotent, runs survive a process restart (resume from the same
file through a fresh saver), and stored bytes carry no AWS credentials —
with a planted-canary control proving the scan can actually fail.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import pytest
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

from cloudpilot.core.config import Settings
from cloudpilot.graph.persistence import create_checkpointer, create_gated_graph
from cloudpilot.graph.state import DeploymentState, DeploymentStatus

# Obviously-fake but correctly-shaped values, like .env.example's. The
# point of the scans is that no value ever put into state or the ambient
# environment reaches the checkpoint file.
_CANARY_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
_CANARY_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
_CANARY_SESSION_TOKEN = "FwoGZXIvYXdzEJr/////////wEXAMPLE"


def _settings_for(path: Path) -> Settings:
    """Deterministic sqlite-backed settings; ambient env and .env ignored."""
    return Settings(checkpoint_backend="sqlite", checkpoint_path=path, _env_file=None)


def _thread_config() -> RunnableConfig:
    return {"configurable": {"thread_id": str(uuid4())}}


def _close(checkpointer: Any) -> None:
    """Close the sqlite connection so bytes are committed before scanning."""
    cast(SqliteSaver, checkpointer).conn.close()


def _raw_checkpoint_bytes(path: Path) -> bytes:
    """Raw bytes of the db plus any WAL/SHM sidecars (deleted rows linger
    in WAL pages until checkpoint — scanning them is stricter, correctly)."""
    chunks = []
    for candidate in (path, Path(f"{path}-wal"), Path(f"{path}-shm")):
        if candidate.exists():
            chunks.append(candidate.read_bytes())
    return b"".join(chunks)


@pytest.mark.unit
def test_factory_defaults_to_in_memory(tmp_path: Path) -> None:
    settings = Settings(_env_file=None)  # no backend override anywhere
    assert settings.checkpoint_backend == "memory"
    assert isinstance(create_checkpointer(settings), InMemorySaver)


@pytest.mark.unit
def test_settings_select_the_sqlite_backend(tmp_path: Path) -> None:
    checkpointer = create_checkpointer(_settings_for(tmp_path / "cloud.db"))
    assert isinstance(checkpointer, SqliteSaver)


@pytest.mark.unit
def test_env_vars_drive_backend_selection(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLOUDPILOT_CHECKPOINT_BACKEND", "sqlite")
    monkeypatch.setenv("CLOUDPILOT_CHECKPOINT_PATH", str(tmp_path / "env.db"))
    assert isinstance(create_checkpointer(Settings(_env_file=None)), SqliteSaver)


@pytest.mark.unit
def test_schema_setup_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "idempotent.db"
    first = cast(SqliteSaver, create_checkpointer(_settings_for(path)))
    first.setup()  # explicit repeat of the factory's setup: a no-op
    second = cast(SqliteSaver, create_checkpointer(_settings_for(path)))  # second connection

    tables = second.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'"
    ).fetchall()
    assert len(tables) == 1


@pytest.mark.unit
def test_run_resumes_across_process_restart(tmp_path: Path) -> None:
    path = tmp_path / "restart.db"
    graph = create_gated_graph(settings=_settings_for(path))
    config = _thread_config()
    graph.invoke(DeploymentState(request="deploy a private S3 bucket").model_dump(), config)
    parked = DeploymentState.model_validate(graph.get_state(config).values)
    _close(graph.checkpointer)

    # "Restart": every in-process object is dropped; only the file survives.
    reopened = create_gated_graph(settings=_settings_for(path))
    snapshot = reopened.get_state(config)
    assert snapshot.next == (DeploymentStatus.DEPLOYING.value,)
    resumed = DeploymentState.model_validate(snapshot.values)
    assert resumed.deployment_id == parked.deployment_id
    assert resumed.status is DeploymentStatus.WAITING_FOR_APPROVAL

    final = reopened.invoke(None, config)
    assert final["status"] is DeploymentStatus.COMPLETED


@pytest.mark.unit
def test_planted_canary_is_detectable_in_stored_bytes(tmp_path: Path) -> None:
    # Sensitivity control for the credential scans below: proves the byte
    # scan reads real checkpoint data and can fail. A secret smuggled into
    # an artifact slot DOES reach the file today — which is exactly why the
    # state contract keeps secrets out of slots (the invariant below).
    path = tmp_path / "canary.db"
    checkpointer = create_checkpointer(_settings_for(path))
    graph = create_gated_graph(settings=_settings_for(path), checkpointer=checkpointer)
    graph.invoke(
        DeploymentState(
            request="deploy a private VPC",
            plan={"aws_secret_access_key": _CANARY_SECRET_ACCESS_KEY},
        ).model_dump(),
        _thread_config(),
    )
    _close(checkpointer)

    assert _CANARY_SECRET_ACCESS_KEY.encode() in _raw_checkpoint_bytes(path)


@pytest.mark.unit
def test_stored_bytes_carry_no_aws_credentials(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Regression tripwire: if a future node or serde path ever dumps the
    # ambient environment or boto3 material into state or metadata, this
    # trips. The canary test above proves the scan is capable of tripping.
    for name, value in (
        ("AWS_ACCESS_KEY_ID", _CANARY_ACCESS_KEY_ID),
        ("AWS_SECRET_ACCESS_KEY", _CANARY_SECRET_ACCESS_KEY),
        ("AWS_SESSION_TOKEN", _CANARY_SESSION_TOKEN),
    ):
        monkeypatch.setenv(name, value)

    path = tmp_path / "clean.db"
    checkpointer = create_checkpointer(_settings_for(path))
    graph = create_gated_graph(settings=_settings_for(path), checkpointer=checkpointer)
    config = _thread_config()
    graph.invoke(DeploymentState(request="deploy a private VPC").model_dump(), config)
    final = graph.invoke(None, config)  # full round trip through every node
    assert final["status"] is DeploymentStatus.COMPLETED
    _close(checkpointer)

    stored = _raw_checkpoint_bytes(path)
    for canary in (_CANARY_ACCESS_KEY_ID, _CANARY_SECRET_ACCESS_KEY, _CANARY_SESSION_TOKEN):
        assert canary.encode() not in stored


@pytest.mark.unit
def test_checkpoint_round_trip_preserves_state_contract(tmp_path: Path) -> None:
    path = tmp_path / "contract.db"
    graph = create_gated_graph(settings=_settings_for(path))
    config = _thread_config()
    graph.invoke(DeploymentState(request="resize the cluster").model_dump(), config)
    _close(graph.checkpointer)

    reopened = create_gated_graph(settings=_settings_for(path))
    reloaded = DeploymentState.model_validate(reopened.get_state(config).values)
    assert reloaded.status is DeploymentStatus.WAITING_FOR_APPROVAL
    assert reloaded.schema_version == 1
    assert reloaded.request == "resize the cluster"
