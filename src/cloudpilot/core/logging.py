"""Centralized, structured logging for CloudPilot.

Every module obtains loggers from :func:`get_logger`; the application
configures output once with :func:`setup_logging`, which emits either JSON
(machine-ingestable) or human-readable text (local development).

Two boundaries this module deliberately sets:

- **Logging is not the audit trail.** Task 033's audit records are typed,
  allowlisted models in their own append-only store. Logs rotate and are
  mutable, so they are unsuitable as the audit of record; the redaction
  below is a safety net for the log stream, not a schema.
- **Secrets never reach a handler.** :class:`SecretRedactionFilter` scrubs
  credential-shaped keys and values (AWS key IDs, bearer tokens, PEM blocks,
  ``key=value`` pairs) from messages, extras, and exception text before
  output. This is defense-in-depth, not a security boundary: call sites
  must still avoid passing secrets, and per ``specs/domains/security.md``
  prompts and model responses are not logged at default levels.

Context fields set with :func:`set_log_context` (``run_id``,
``request_id``, ``actor`` …) are attached to every JSON record so later
tasks can distinguish agent runs and requests without threading ids
through every call.
"""

from __future__ import annotations

import json
import logging
import re
import sys
import traceback
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any, TextIO

REDACTED = "***REDACTED***"

# A key matching any of these substrings has its value redacted.
_SENSITIVE_KEY = re.compile(
    r"secret|token|password|credential|api[_-]?key|authorization|access[_-]?key|external[_-]?id",
    re.IGNORECASE,
)

# Value patterns scrubbed from free text, applied in order. Group 1 in the
# key/value pattern preserves the key name so logs stay diagnosable.
_TEXT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    # Private key blocks (multi-line).
    (
        re.compile(
            r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
        REDACTED,
    ),
    # AWS access key ids: AKIA… (long-term), ASIA… (STS temporary), AIDA/AROA.
    (re.compile(r"\b(?:AKIA|ASIA|AIDA|AROA)[0-9A-Z]{16}\b"), REDACTED),
    # Bearer tokens: "Bearer eyJ…".
    (re.compile(r"\b[Bb]earer\s+[A-Za-z0-9\-._~+/]+=*"), f"Bearer {REDACTED}"),
    # Credentials embedded in URLs: "https://user:pass@host".
    (re.compile(r"://[^/\s:@]+:[^/\s@]+@"), f"://{REDACTED}@"),
    # key=value / "key": "value" pairs for credential-shaped keys.
    (
        re.compile(
            r"([\"']?(?:aws_access_key_id|aws_secret_access_key|aws_session_token|secret|password|token|api_key|external_id)[\"']?)"
            r"(\s*[=:]\s*)[\"']?[^\s\"',;}]+[\"']?",
            re.IGNORECASE,
        ),
        rf"\1\2{REDACTED}",
    ),
)

# Attributes the logging module itself populates; everything else on a
# record's __dict__ came from ``extra=`` or LogRecord factory defaults.
_STANDARD_ATTRS = frozenset(logging.makeLogRecord({}).__dict__) | {"message", "asctime", "exc_text"}

_log_context: ContextVar[dict[str, str] | None] = ContextVar("cloudpilot_log_context", default=None)


def redact_text(text: str) -> str:
    """Return ``text`` with credential-shaped values replaced."""
    for pattern, replacement in _TEXT_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def _is_sensitive_key(key: str) -> bool:
    return bool(_SENSITIVE_KEY.search(key))


def redact_mapping(data: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of ``data`` with sensitive keys and text values redacted."""
    redacted: dict[str, Any] = {}
    for key, value in data.items():
        if _is_sensitive_key(key):
            redacted[key] = REDACTED
        elif isinstance(value, dict):
            redacted[key] = redact_mapping(value)
        elif isinstance(value, list):
            redacted[key] = [
                redact_mapping(item) if isinstance(item, dict) else item for item in value
            ]
        elif isinstance(value, str):
            redacted[key] = redact_text(value)
        else:
            redacted[key] = value
    return redacted


class SecretRedactionFilter(logging.Filter):
    """Scrubs credential-shaped data from records in place, before any handler.

    Mutating the record (rather than only the rendered output) means every
    formatter — including ones attached by other handlers later — sees
    redacted data.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_text(record.getMessage())
        record.args = ()
        if record.exc_info is not None:
            record.exc_text = redact_text("".join(traceback.format_exception(*record.exc_info)))
        for key, value in list(record.__dict__.items()):
            if key in {"msg", "args", "exc_text", "exc_info", "stack_info"}:
                continue
            if _is_sensitive_key(key):
                record.__dict__[key] = REDACTED
            elif isinstance(value, str):
                record.__dict__[key] = redact_text(value)
        return True


class JsonFormatter(logging.Formatter):
    """One JSON object per record: timestamp, level, logger, message, extras."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_text(record.getMessage()),
        }
        extras = {
            key: value for key, value in record.__dict__.items() if key not in _STANDARD_ATTRS
        }
        payload.update(redact_mapping(extras))
        context = get_log_context()
        if context:
            payload.update(redact_mapping(context))
        if record.exc_info is not None:
            payload["exception"] = redact_text(self.formatException(record.exc_info))
        if record.stack_info:
            payload["stack"] = record.stack_info
        return json.dumps(payload, default=str)


class HumanFormatter(logging.Formatter):
    """Single-line human-readable output with the same redaction guarantees."""

    def __init__(self) -> None:
        super().__init__("%(asctime)s %(levelname)s %(name)s %(message)s")

    def format(self, record: logging.LogRecord) -> str:
        return redact_text(super().format(record))


class RootLogHandler(logging.StreamHandler[TextIO]):
    """Handler owned by :func:`setup_logging`.

    Tagged by class so re-running setup removes exactly its own handlers and
    leaves handlers attached by other libraries untouched.
    """


def get_logger(name: str) -> logging.Logger:
    """Return the named logger. Handlers come from :func:`setup_logging` only."""
    return logging.getLogger(name)


def setup_logging(
    *, level: str = "INFO", json_output: bool = True, stream: TextIO | None = None
) -> None:
    """Configure the root logger exactly once per process invocation.

    Idempotent: re-running removes only handlers this function previously
    attached, leaving handlers other libraries added untouched. ``stream``
    exists for tests; production logs go to stderr.

    Raises ``ValueError`` for an unknown level so misconfiguration fails
    fast at startup rather than silently defaulting.
    """
    numeric_level = logging.getLevelNamesMapping().get(level.upper())
    if numeric_level is None:
        raise ValueError(f"unknown log level: {level!r}")

    root = logging.getLogger()
    root.setLevel(numeric_level)
    for handler in [h for h in root.handlers if isinstance(h, RootLogHandler)]:
        root.removeHandler(handler)
        handler.close()

    handler = RootLogHandler(stream if stream is not None else sys.stderr)
    handler.setFormatter(JsonFormatter() if json_output else HumanFormatter())
    handler.addFilter(SecretRedactionFilter())
    root.addHandler(handler)


def set_log_context(**fields: str) -> None:
    """Attach context (run_id, request_id, actor …) to subsequent records."""
    merged = dict(_log_context.get() or {})
    merged.update(fields)
    _log_context.set(merged)


def get_log_context() -> dict[str, str]:
    """Return a copy of the current log context."""
    return dict(_log_context.get() or {})


def clear_log_context() -> None:
    """Drop all context fields (test isolation and request boundaries)."""
    _log_context.set({})
