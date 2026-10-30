# Development

How to set up, validate, and manually verify CloudPilot. Every command here
was run against this repository; the automated checks are offline and
deterministic by convention (see `tests/conftest.py`).

## Prerequisites

| Need | Used by | Notes |
|---|---|---|
| `uv` | everything | Manages the Python 3.12 venv. `python3 -m pip install --user uv` if missing |
| Docker + Compose | Task 006 checks | Only for the container checks below |
| AWS credentials (ambient) | live Task 007 checks only | Optional — the test suite never needs them |

## Setup

```bash
make install    # uv venv (Python 3.12) + editable install + dev tools
```

Optional git hooks (run the same ruff/mypy binaries as `make`):

```bash
uvx pre-commit install
```

## Standard checks

```bash
make lint        # ruff check + ruff format --check
make format      # apply ruff format
make typecheck   # mypy --strict over src/ and tests/
make test        # full pytest suite (offline, no credentials needed)
```

Run everything at once:

```bash
make lint && make typecheck && make test
```

## Manual verification per task

### 002 — Dev environment

```bash
make lint && make typecheck && make test
uvx pre-commit run --all-files      # the wired ruff + mypy hooks
```

The import-direction contract (README table) is enforced by an AST check:

```bash
.venv/bin/python -m pytest tests/test_import_direction.py -v
```

### 003 — Logging

```bash
.venv/bin/python -m pytest tests/test_logging.py -v
```

Live demo — JSON output with a secret redacted (writes to stderr):

```bash
.venv/bin/python -c "
from cloudpilot.core.logging import setup_logging, get_logger
setup_logging(level='INFO', json_output=True)
log = get_logger('demo')
log.info('connecting', extra={'aws_secret_access_key': 'SHOULD-NOT-APPEAR', 'region': 'eu-west-1'})
"
```

Expected: one JSON line with `"aws_secret_access_key": "***REDACTED***"`
and `"region": "eu-west-1"`. Add `json_output=False` for human-readable mode.

### 004 — Configuration

```bash
.venv/bin/python -m pytest tests/test_config.py -v

# Environment variable beats the default:
CLOUDPILOT_AWS_REGION=eu-west-1 .venv/bin/python -c \
  "from cloudpilot.core.config import get_settings; print(get_settings())"

# .env file (gitignored — remove it afterwards):
cp .env.example .env
.venv/bin/python -c "from cloudpilot.core.config import get_settings; print(get_settings())"
rm .env
```

Misconfiguration fails fast:

```bash
CLOUDPILOT_LOG_LEVEL=LOUD .venv/bin/python -c \
  "from cloudpilot.core.config import get_settings; get_settings()"   # ValueError
```

### 007 — AWS authentication

Offline — STS stubbed, no credentials, no network (safe anywhere):

```bash
.venv/bin/python -m pytest tests/test_aws.py -v
```

Live — read-only STS call against your ambient credentials (prints account
and role ARN, never secret values):

```bash
# Ambient credentials path:
.venv/bin/python -c "
from cloudpilot.core.aws import get_session
print(get_session().client('sts').get_caller_identity())
"

# Assumed-role path (your ambient creds assume the role):
CLOUDPILOT_AWS_ROLE_ARN=arn:aws:iam::<ACCOUNT>:role/<ROLE> .venv/bin/python -c "
from cloudpilot.core.aws import get_session
print(get_session().client('sts').get_caller_identity())
"
```

Typed failure instead of a confusing boto3 trace:

```bash
env -i PATH=$PATH .venv/bin/python -c "from cloudpilot.core.aws import get_session; get_session()"
# → CredentialsNotFoundError: no ambient AWS credentials found (...)
```

### 006 — Docker

```bash
docker compose up -d --build
curl http://127.0.0.1:8010/health     # → {"status":"ok"}
docker compose ps                     # app and checkpoint-db both "healthy"
docker compose exec app id -u         # → 1000 (non-root runtime user)
docker compose logs -f app            # uvicorn serving; Ctrl-C stops following
docker compose down -v                # tear down, remove the dev volume
```

The `healthy` status is the image's own HEALTHCHECK (a urllib request to
`/health` from inside the container). Host port **8010** was chosen because
port 8000 was already taken on the build machine — change the mapping in
`docker-compose.yml` if your 8000 is free.

## Things that touch the network

Only two: `docker compose up` (image pulls) and the live AWS commands in
007. Everything else — including the whole test suite — is fully offline.

## Conventions worth knowing

- **`uv.lock` is deliberately gitignored** and dependencies are unpinned
  until the pinning follow-up task (see AGENTS.md). Don't commit it.
- **Never put AWS credentials in `.env`, compose files, or the image.**
  They come from the ambient environment at runtime; `core/aws.py` never
  generates or persists them.
- **Per-task rationale lives in the git history** — each task landed as
  its own commit explaining its decisions.
