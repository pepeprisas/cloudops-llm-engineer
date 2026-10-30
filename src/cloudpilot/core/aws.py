"""AWS session factory: ambient credentials or STS role assumption.

Hard rule (AGENTS.md): this module NEVER generates, mints, or persists AWS
credentials. It only reads ambient ones (boto3's credential chain: env,
shared credentials file, instance role) or exchanges them for temporary
assumed-role credentials via STS ``assume_role``. Assumed credentials live
only in the returned ``boto3.Session`` object — never in ``os.environ``,
files, or ``Settings``.

Consequence for Task 019: MCP servers must obtain sessions in-process from
this factory, not by injecting assumed credentials into the environment.

Failure modes are typed (see below) so callers can distinguish "nothing to
assume from" from "assumption was denied" without parsing strings. Error
messages carry role/session metadata only — never credential values.
"""

from __future__ import annotations

import re
from typing import Any, Protocol

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from cloudpilot.core.config import Settings, get_settings
from cloudpilot.core.logging import get_logger

_logger = get_logger(__name__)

_SESSION_NAME_ALLOWED = re.compile(r"[^\w+=,.@-]")


class CloudPilotAWSError(Exception):
    """Base class for CloudPilot AWS authentication failures."""


class CredentialsNotFoundError(CloudPilotAWSError):
    """No ambient AWS credentials exist to build a session from."""


class RoleAssumptionError(CloudPilotAWSError):
    """STS ``assume_role`` failed or returned an unusable response."""

    def __init__(
        self, message: str, *, code: str | None = None, request_id: str | None = None
    ) -> None:
        super().__init__(message)
        self.code = code
        self.request_id = request_id


class STSClient(Protocol):
    """The slice of a boto3 STS client this module uses (test seam)."""

    def assume_role(self, **kwargs: Any) -> dict[str, Any]: ...


def _session_name(name: str | None) -> str:
    """Sanitize to STS's RoleSessionName charset [\\w+=,.@-]{2,64}."""
    candidate = name or "cloudpilot-session"
    sanitized = _SESSION_NAME_ALLOWED.sub("-", candidate)
    sanitized = re.sub(r"-{2,}", "-", sanitized).strip("-")[:64]
    return sanitized if len(sanitized) >= 2 else "cloudpilot-session"


def get_session(
    settings: Settings | None = None,
    *,
    sts_client: STSClient | None = None,
    session_name: str | None = None,
) -> boto3.Session:
    """Return a session using ambient credentials or an assumed role.

    - No ``settings.aws_role_arn``: verify ambient credentials exist (eager,
      so failure surfaces here rather than mid-workflow) and return the
      ambient session.
    - Role configured: STS ``assume_role`` with the scoped duration and,
      only when configured, the external id; return a session built from
      the in-memory temporary credentials.

    Raises:
        CredentialsNotFoundError: no ambient credentials are available.
        RoleAssumptionError: STS denied the request or returned an
            unusable response.

    ``sts_client`` exists so tests can attach a botocore ``Stubber``;
    production callers never pass it.
    """
    cfg = settings if settings is not None else get_settings()
    base = boto3.Session(profile_name=cfg.aws_profile, region_name=cfg.aws_region)

    if cfg.aws_role_arn is None:
        if base.get_credentials() is None:
            raise CredentialsNotFoundError(
                "no ambient AWS credentials found (environment, shared credentials file, or instance role)"
            )
        return base

    if base.get_credentials() is None:
        raise CredentialsNotFoundError(
            "cannot assume role: no ambient credentials available for STS"
        )

    client: STSClient = sts_client if sts_client is not None else base.client("sts")
    params: dict[str, Any] = {
        "RoleArn": cfg.aws_role_arn,
        "RoleSessionName": _session_name(session_name),
        "DurationSeconds": cfg.aws_sts_duration_seconds,
    }
    if cfg.aws_sts_external_id is not None:
        params["ExternalId"] = cfg.aws_sts_external_id

    try:
        response = client.assume_role(**params)
    except ClientError as exc:
        error = exc.response.get("Error", {})
        raise RoleAssumptionError(
            f"assume_role failed for {cfg.aws_role_arn}: {error.get('Code', 'Unknown')} "
            f"({error.get('Message', 'no message')})",
            code=error.get("Code"),
            request_id=exc.response.get("ResponseMetadata", {}).get("RequestId"),
        ) from None  # chaining excluded: ClientError context can echo request data
    except NoCredentialsError:
        raise CredentialsNotFoundError(
            "STS credentials disappeared before the assume_role call"
        ) from None

    credentials = response.get("Credentials") or {}
    try:
        session = boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
            region_name=cfg.aws_region,
        )
    except KeyError as exc:
        # from None: never chain the credential-bearing response into a traceback.
        raise RoleAssumptionError(f"assume_role response missing field: {exc}") from None

    # Metadata only — never the credential values themselves.
    _logger.debug(
        "assumed role via STS",
        extra={"role_arn": cfg.aws_role_arn, "session_name": params["RoleSessionName"]},
    )
    return session
