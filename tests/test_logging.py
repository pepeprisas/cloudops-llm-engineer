"""Unit tests for the logging module: formatting, redaction, idempotence."""

from __future__ import annotations

import io
import json
import logging
from collections.abc import Iterator
from datetime import datetime

import pytest

from cloudpilot.core.logging import (
    REDACTED,
    RootLogHandler,
    SecretRedactionFilter,
    clear_log_context,
    get_log_context,
    get_logger,
    redact_mapping,
    redact_text,
    set_log_context,
    setup_logging,
)

FAKE_AWS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
FAKE_STS_KEY_ID = "ASIAIOSFODNN7EXAMPLE"
FAKE_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


@pytest.fixture(autouse=True)
def _isolate_root_logger_and_context() -> Iterator[None]:
    """Restore global logger and context state after every test."""
    root = logging.getLogger()
    handlers, level, propagate = root.handlers[:], root.level, root.propagate
    clear_log_context()
    yield
    root.handlers[:] = handlers
    root.setLevel(level)
    root.propagate = propagate
    clear_log_context()


def _capture(
    *, level: str = "INFO", json_output: bool = True
) -> tuple[logging.Logger, io.StringIO]:
    buffer = io.StringIO()
    setup_logging(level=level, json_output=json_output, stream=buffer)
    return get_logger("cloudpilot.test.logging"), buffer


@pytest.mark.unit
def test_get_logger_returns_named_logger() -> None:
    logger = get_logger("cloudpilot.core.example")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "cloudpilot.core.example"


@pytest.mark.unit
def test_json_output_has_required_fields_and_extras() -> None:
    logger, buffer = _capture()
    logger.info("deployment started", extra={"deployment_id": "d-1"})

    record = json.loads(buffer.getvalue())
    assert record["message"] == "deployment started"
    assert record["level"] == "INFO"
    assert record["logger"] == "cloudpilot.test.logging"
    assert record["deployment_id"] == "d-1"
    # Timestamp must be present and ISO-parseable; raises ValueError if not.
    datetime.fromisoformat(record["timestamp"])


@pytest.mark.unit
def test_human_output_is_plain_text_not_json() -> None:
    logger, buffer = _capture(json_output=False)
    logger.warning("carry on")

    output = buffer.getvalue()
    assert "carry on" in output
    assert "WARNING" in output
    with pytest.raises(json.JSONDecodeError):
        json.loads(output)


@pytest.mark.unit
def test_unknown_level_fails_fast() -> None:
    with pytest.raises(ValueError, match="unknown log level"):
        setup_logging(level="LOUD")


@pytest.mark.unit
@pytest.mark.parametrize(
    "secret",
    [
        FAKE_AWS_KEY_ID,
        FAKE_STS_KEY_ID,
        f"aws_secret_access_key={FAKE_SECRET}",
        '"aws_session_token": "FwoGZXIvYXdzEJr//////////wEXAMPLE"',
        "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.abc123",
        "https://user:hunter2@example.internal/api",
        "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA\n-----END RSA PRIVATE KEY-----",
    ],
)
def test_redact_text_masks_credential_shapes(secret: str) -> None:
    redacted = redact_text(f"connecting with {secret} now")
    assert secret not in redacted
    assert REDACTED in redacted


@pytest.mark.unit
def test_redact_mapping_masks_sensitive_keys_recursively() -> None:
    data = {
        "aws_access_key_id": FAKE_AWS_KEY_ID,
        "region": "eu-west-1",
        "nested": {"password": "hunter2", "count": 3},
        "note": f"key is {FAKE_AWS_KEY_ID}",
    }
    redacted = redact_mapping(data)
    assert redacted["aws_access_key_id"] == REDACTED
    assert redacted["region"] == "eu-west-1"
    assert redacted["nested"]["password"] == REDACTED
    assert redacted["nested"]["count"] == 3
    assert FAKE_AWS_KEY_ID not in redacted["note"]


@pytest.mark.unit
def test_end_to_end_log_contains_no_secret() -> None:
    logger, buffer = _capture()
    logger.error(
        "assume-role failed",
        extra={
            "aws_secret_access_key": FAKE_SECRET,
            "role_arn": "arn:aws:iam::123456789012:role/dev",
        },
        exc_info=None,
    )
    output = buffer.getvalue()
    assert FAKE_SECRET not in output
    assert REDACTED in output
    assert "arn:aws:iam::123456789012:role/dev" in output  # ARNs are not secrets


@pytest.mark.unit
def test_exception_text_is_redacted() -> None:
    logger, buffer = _capture()
    try:
        raise RuntimeError(f"sts rejected {FAKE_AWS_KEY_ID}")
    except RuntimeError:
        logger.error("call failed", exc_info=True)

    output = buffer.getvalue()
    assert FAKE_AWS_KEY_ID not in output
    assert REDACTED in output
    assert "RuntimeError" in output  # the failure itself stays diagnosable


@pytest.mark.unit
def test_context_fields_attach_to_json_records() -> None:
    logger, buffer = _capture()
    set_log_context(run_id="run-42", request_id="req-7")
    try:
        logger.info("planning")
        assert get_log_context() == {"run_id": "run-42", "request_id": "req-7"}
    finally:
        clear_log_context()

    record = json.loads(buffer.getvalue())
    assert record["run_id"] == "run-42"
    assert record["request_id"] == "req-7"


@pytest.mark.unit
def test_setup_logging_is_idempotent() -> None:
    _, buffer = _capture()
    _capture()  # second setup must replace, not stack, our handler
    root = logging.getLogger()
    ours = [h for h in root.handlers if isinstance(h, RootLogHandler)]
    assert len(ours) == 1

    get_logger("cloudpilot.test.logging").info("after re-setup")
    assert buffer.getvalue() == ""  # old handler detached, its buffer sees nothing


@pytest.mark.unit
def test_foreign_handlers_survive_setup() -> None:
    root = logging.getLogger()
    foreign = logging.StreamHandler(io.StringIO())
    root.addHandler(foreign)
    _capture()
    assert foreign in root.handlers


@pytest.mark.unit
def test_filter_alone_scrubs_a_record() -> None:
    record = logging.LogRecord(
        name="cloudpilot.test",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="token=%s",
        args=(FAKE_SECRET,),
        exc_info=None,
    )
    assert SecretRedactionFilter().filter(record) is True
    assert FAKE_SECRET not in record.getMessage()
    assert REDACTED in record.getMessage()
