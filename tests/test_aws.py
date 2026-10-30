"""Unit tests for the AWS session factory (STS stubbed, no network)."""

from __future__ import annotations

import io
import json
import logging
import os
from collections.abc import Iterator
from datetime import UTC, datetime

import boto3
import pytest
from botocore.exceptions import UnStubbedResponseError
from botocore.stub import Stubber

from cloudpilot.core.aws import (
    CredentialsNotFoundError,
    RoleAssumptionError,
    get_session,
)
from cloudpilot.core.config import Settings, get_settings
from cloudpilot.core.logging import setup_logging

ROLE_ARN = "arn:aws:iam::123456789012:role/cloudpilot-dev"
ASSUMED_ACCESS_KEY = "ASIAIOSFODNN7EXAMPLE"
ASSUMED_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
ASSUMED_TOKEN = "FwoGZXIvYXdzEJr//////////wEXAMPLE"


def _assume_role_response() -> dict[str, object]:
    return {
        "Credentials": {
            "AccessKeyId": ASSUMED_ACCESS_KEY,
            "SecretAccessKey": ASSUMED_SECRET,
            "SessionToken": ASSUMED_TOKEN,
            "Expiration": datetime(2030, 1, 1, tzinfo=UTC),
        },
        "AssumedRoleUser": {
            "AssumedRoleId": "AROAEXAMPLE:cloudpilot-session",
            "Arn": "arn:aws:sts::123456789012:assumed-role/cloudpilot-dev/cloudpilot-session",
        },
    }


@pytest.fixture(autouse=True)
def _isolated_aws_environment(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Deterministic, network-free AWS env for every test in this module.

    IMDS disabled so nothing probes the metadata endpoint; a nonexistent
    shared-credentials path so a developer's real ~/.aws never leaks in;
    dummy env creds so the ambient path is deterministic.
    """
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", "/nonexistent/cloudpilot-test-credentials")
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    get_settings.cache_clear()
    yield
    root.handlers[:] = handlers
    root.setLevel(level)
    get_settings.cache_clear()


def _no_ambient_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_PROFILE"):
        monkeypatch.delenv(key, raising=False)


@pytest.mark.unit
def test_ambient_session_is_returned_when_no_role_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "TESTACCESSKEYID000EX")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "ambient-secret")

    session = get_session(Settings(_env_file=None))

    assert session.get_credentials() is not None
    assert session.get_credentials().access_key == "TESTACCESSKEYID000EX"
    assert session.region_name == "us-east-1"


@pytest.mark.unit
def test_missing_ambient_credentials_raise_typed_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _no_ambient_credentials(monkeypatch)

    with pytest.raises(CredentialsNotFoundError, match="no ambient AWS credentials"):
        get_session(Settings(_env_file=None))


@pytest.mark.unit
def test_missing_ambient_credentials_raise_even_with_role_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # STS itself needs ambient credentials to sign the request; fail eagerly
    # at the factory instead of mid-workflow.
    _no_ambient_credentials(monkeypatch)

    with pytest.raises(CredentialsNotFoundError, match="cannot assume role"):
        get_session(Settings(_env_file=None, aws_role_arn=ROLE_ARN))


@pytest.mark.unit
def test_assume_role_returns_scoped_session_and_matches_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "TESTACCESSKEYID000EX")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "ambient-secret")
    sts = boto3.client("sts", region_name="us-east-1")
    stubber = Stubber(sts)
    # Stubber asserts the exact request params — including that no
    # ExternalId is sent when none is configured.
    stubber.add_response(
        "assume_role",
        _assume_role_response(),
        expected_params={
            "RoleArn": ROLE_ARN,
            "RoleSessionName": "cloudpilot-session",
            "DurationSeconds": 3600,
        },
    )
    stubber.activate()

    session = get_session(Settings(_env_file=None, aws_role_arn=ROLE_ARN), sts_client=sts)

    credentials = session.get_credentials()
    assert credentials is not None
    assert credentials.access_key == ASSUMED_ACCESS_KEY
    assert session.region_name == "us-east-1"
    stubber.deactivate()


@pytest.mark.unit
def test_external_id_is_sent_only_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "TESTACCESSKEYID000EX")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "ambient-secret")
    sts = boto3.client("sts", region_name="us-east-1")
    stubber = Stubber(sts)
    stubber.add_response(
        "assume_role",
        _assume_role_response(),
        expected_params={
            "RoleArn": ROLE_ARN,
            "RoleSessionName": "deploy-run-42",
            "DurationSeconds": 900,
            "ExternalId": "operator-external-id",
        },
    )
    stubber.activate()

    settings = Settings(
        _env_file=None,
        aws_role_arn=ROLE_ARN,
        aws_sts_external_id="operator-external-id",
        aws_sts_duration_seconds=900,
    )
    get_session(settings, sts_client=sts, session_name="deploy/run 42!")

    stubber.deactivate()  # would raise StubAssertionError on param mismatch


@pytest.mark.unit
def test_assumed_credentials_are_never_persisted_to_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "TESTACCESSKEYID000EX")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "ambient-secret")
    before = dict(os.environ)
    sts = boto3.client("sts", region_name="us-east-1")
    stubber = Stubber(sts)
    stubber.add_response("assume_role", _assume_role_response())
    stubber.activate()

    get_session(Settings(_env_file=None, aws_role_arn=ROLE_ARN), sts_client=sts)

    assert dict(os.environ) == before
    assert ASSUMED_SECRET not in str(dict(os.environ))


@pytest.mark.unit
def test_assume_role_denial_raises_typed_error_with_safe_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "TESTACCESSKEYID000EX")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "ambient-secret")
    sts = boto3.client("sts", region_name="us-east-1")
    stubber = Stubber(sts)
    stubber.add_client_error(
        "assume_role",
        service_error_code="AccessDenied",
        service_message="not authorized to perform sts:AssumeRole",
        http_status_code=403,
    )
    stubber.activate()

    with pytest.raises(RoleAssumptionError) as excinfo:
        get_session(Settings(_env_file=None, aws_role_arn=ROLE_ARN), sts_client=sts)

    assert excinfo.value.code == "AccessDenied"
    assert "AccessDenied" in str(excinfo.value)
    assert ROLE_ARN in str(excinfo.value)
    assert "ambient-secret" not in str(excinfo.value)


@pytest.mark.unit
def test_malformed_assume_role_response_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "TESTACCESSKEYID000EX")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "ambient-secret")
    sts = boto3.client("sts", region_name="us-east-1")
    stubber = Stubber(sts)
    stubber.add_response("assume_role", {})
    stubber.activate()

    with pytest.raises(RoleAssumptionError, match="missing field"):
        get_session(Settings(_env_file=None, aws_role_arn=ROLE_ARN), sts_client=sts)


@pytest.mark.unit
def test_unstubbed_call_fails_the_test_loudly(monkeypatch: pytest.MonkeyPatch) -> None:
    # Guard against the seam silently reaching the network: an active
    # stubber with no queued response must reject the call.
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "TESTACCESSKEYID000EX")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "ambient-secret")
    sts = boto3.client("sts", region_name="us-east-1")
    stubber = Stubber(sts)
    stubber.activate()

    with pytest.raises(UnStubbedResponseError):
        get_session(Settings(_env_file=None, aws_role_arn=ROLE_ARN), sts_client=sts)


@pytest.mark.unit
def test_session_creation_logs_no_credential_material(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "TESTACCESSKEYID000EX")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "ambient-secret")
    buffer = io.StringIO()
    # JSON output so extras (role_arn, session_name) are part of the record.
    setup_logging(level="DEBUG", json_output=True, stream=buffer)
    sts = boto3.client("sts", region_name="us-east-1")
    stubber = Stubber(sts)
    stubber.add_response("assume_role", _assume_role_response())
    stubber.activate()

    get_session(Settings(_env_file=None, aws_role_arn=ROLE_ARN), sts_client=sts)

    output = buffer.getvalue()
    # botocore DEBUG records share the handler; pick ours out per-line.
    record = next(
        json.loads(line) for line in output.splitlines() if '"cloudpilot.core.aws"' in line
    )
    assert record["role_arn"] == ROLE_ARN  # role metadata is fine to log
    assert record["session_name"] == "cloudpilot-session"
    # Redaction covers every record through the handler, botocore's included.
    assert ASSUMED_ACCESS_KEY not in output
    assert ASSUMED_SECRET not in output
    assert ASSUMED_TOKEN not in output
    assert "ambient-secret" not in output
