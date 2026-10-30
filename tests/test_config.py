"""Unit tests for Settings: sources, validation, and credential exclusion."""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError

from cloudpilot.core.config import Settings, get_settings

# Field names that would smuggle credentials into settings. A field matching
# any of these is a regression of the "never generate or persist AWS
# credentials" hard rule.
CREDENTIAL_FIELD_DENYLIST = re.compile(
    r"access_key|secret|password|token|credential", re.IGNORECASE
)

VALID_ROLE_ARN = "arn:aws:iam::123456789012:role/cloudpilot-dev"


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.unit
def test_defaults_are_defined_and_safe() -> None:
    settings = Settings(_env_file=None)
    assert settings.log_level == "INFO"
    assert settings.log_json is True
    assert settings.aws_region == "us-east-1"
    assert settings.aws_profile is None
    assert settings.aws_role_arn is None
    assert settings.aws_sts_external_id is None
    assert settings.aws_sts_duration_seconds == 3600


@pytest.mark.unit
def test_loads_from_prefixed_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLOUDPILOT_AWS_REGION", "eu-west-1")
    monkeypatch.setenv("CLOUDPILOT_LOG_JSON", "false")
    monkeypatch.setenv("CLOUDPILOT_AWS_ROLE_ARN", VALID_ROLE_ARN)

    settings = Settings(_env_file=None)
    assert settings.aws_region == "eu-west-1"
    assert settings.log_json is False
    assert settings.aws_role_arn == VALID_ROLE_ARN


@pytest.mark.unit
def test_unprefixed_env_vars_are_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    # A bare AWS_* variable must not leak into settings: boto3 owns those.
    monkeypatch.setenv("AWS_REGION", "ap-southeast-2")
    settings = Settings(_env_file=None)
    assert settings.aws_region == "us-east-1"


@pytest.mark.unit
def test_loads_from_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("CLOUDPILOT_LOG_LEVEL=DEBUG\n")

    settings = Settings(_env_file=env_file)
    assert settings.log_level == "DEBUG"


@pytest.mark.unit
def test_credential_fields_are_forbidden() -> None:
    # mypy statically forbids this kwarg (the point of extra="forbid"), so
    # the runtime rejection is asserted through an Any-typed dict.
    smuggled = cast(dict[str, Any], {"aws_secret_access_key": "should-never-work"})
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **smuggled)


@pytest.mark.unit
def test_no_field_name_looks_like_a_credential() -> None:
    # Guards against someone adding aws_access_key_id "for convenience".
    offenders = [name for name in Settings.model_fields if CREDENTIAL_FIELD_DENYLIST.search(name)]
    assert offenders == []


@pytest.mark.unit
def test_repr_is_safe_to_log() -> None:
    # Invariant relied on by later tasks: repr(Settings) never contains
    # credential material because no credential fields exist at all.
    representation = repr(Settings(_env_file=None))
    assert "key" not in representation.lower()
    assert "secret" not in representation.lower()


@pytest.mark.unit
@pytest.mark.parametrize(
    "arn",
    [
        "arn:aws:iam::123:role/short-account",
        "arn:aws:iam::123456789012:role/bad*role",  # wildcard
        "arn:aws:iam::123456789012:role/bad role",  # space
        "arn:aws:s3:::my-bucket",  # not an IAM role
    ],
)
def test_invalid_role_arns_are_rejected(arn: str) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, aws_role_arn=arn)


@pytest.mark.unit
def test_role_path_in_arn_is_accepted() -> None:
    settings = Settings(
        _env_file=None, aws_role_arn="arn:aws:iam::123456789012:role/team/cloudpilot"
    )
    assert settings.aws_role_arn is not None


@pytest.mark.unit
@pytest.mark.parametrize("seconds", [899, 3601])
def test_sts_duration_is_bounded(seconds: int) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, aws_sts_duration_seconds=seconds)


@pytest.mark.unit
@pytest.mark.parametrize("seconds", [900, 3600])
def test_sts_duration_bounds_are_inclusive(seconds: int) -> None:
    settings = Settings(_env_file=None, aws_sts_duration_seconds=seconds)
    assert settings.aws_sts_duration_seconds == seconds


@pytest.mark.unit
def test_invalid_log_level_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, log_level="LOUD")


@pytest.mark.unit
def test_invalid_region_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, aws_region="east-1")


@pytest.mark.unit
def test_get_settings_is_a_cached_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    first = get_settings()
    assert get_settings() is first

    monkeypatch.setenv("CLOUDPILOT_AWS_REGION", "eu-central-1")
    get_settings.cache_clear()
    refreshed = get_settings()
    assert refreshed is not first
    assert refreshed.aws_region == "eu-central-1"
