"""Centralized application settings.

One typed :class:`Settings` object, loaded from ``CLOUDPILOT_``-prefixed
environment variables and an optional ``.env`` file, is the single source of
configuration for every module.

Design boundaries:

- **Env prefix.** Fields map to ``CLOUDPILOT_*`` variables, never bare
  ``AWS_*`` names: ambient AWS credentials are resolved by boto3's own
  credential chain (Task 007), and unprefixed field names would collide
  with unrelated ambient variables and silently change behavior.
- **No credential fields, ever.** ``extra="forbid"`` plus a unit test over
  ``model_fields`` guarantee credentials cannot be smuggled in through the
  environment; ``repr(Settings)`` is safe to log. Secrets come from the
  ambient environment or STS, not from settings.
- **The role ARN is untrusted input**, not a secret: it is shape-validated
  (no wildcards, bounded length) because env substitution of a role ARN is
  a credential-redirection vector.
"""

from __future__ import annotations

from functools import cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Full ARN, 12-digit account id, role path without wildcards or spaces.
_ROLE_ARN_PATTERN = r"^arn:aws[a-zA-Z-]*:iam::\d{12}:role/[A-Za-z0-9+=,.@\-_/]+$"


class Settings(BaseSettings):
    """Typed application settings with validated fields and safe defaults."""

    model_config = SettingsConfigDict(
        env_prefix="CLOUDPILOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    # Logging (consumed by cloudpilot.core.logging's setup_logging).
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_json: bool = True

    # AWS. Region and role feed the session factory in core.aws (Task 007).
    aws_region: str = Field(default="us-east-1", pattern=r"^[a-z]{2}(-gov)?-[a-z]+-\d$")
    aws_profile: str | None = None
    aws_role_arn: str | None = Field(default=None, pattern=_ROLE_ARN_PATTERN, max_length=2048)
    # External id for the role's trust policy: operator-supplied at deploy
    # time, semi-secret, never a committed real value.
    aws_sts_external_id: str | None = Field(default=None, min_length=1, max_length=128)
    aws_sts_duration_seconds: int = Field(default=3600, ge=900, le=3600)


@cache
def get_settings() -> Settings:
    """Return the process-wide settings singleton.

    Cached; tests must call ``get_settings.cache_clear()`` around
    environment mutations (see ``tests/test_config.py``).
    """
    return Settings()
