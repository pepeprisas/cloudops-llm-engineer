"""Unit tests for the minimal API app (Task 006's health check contract)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from cloudpilot.api.app import create_app


def _client() -> TestClient:
    return TestClient(create_app())


@pytest.mark.unit
def test_health_returns_200_ok() -> None:
    response = _client().get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.unit
def test_health_discloses_nothing_beyond_status() -> None:
    # The endpoint is unauthenticated, so it must stay status-only: no
    # config, versions, ARNs, or host detail.
    assert set(_client().get("/health").json()) == {"status"}


@pytest.mark.unit
def test_unknown_paths_404() -> None:
    assert _client().get("/definitely-not-a-route").status_code == 404
