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

### 008 — Deployment state model

```bash
.venv/bin/python -m pytest tests/test_state.py -v
```

The state contract enforces the deployment state machine, frozen models, and
credential-free field names:

```bash
.venv/bin/python -c "
from cloudpilot.graph.state import DeploymentState, DeploymentStatus
s = DeploymentState(request='deploy a bucket')
print('status:', s.status)  # → REQUEST_RECEIVED
print('deployment_id:', s.deployment_id)
print('events:', s.events)  # → []
print('schema_version:', s.schema_version)  # → 1
"
```

Expected: `status` is `REQUEST_RECEIVED`, `deployment_id` is a UUID, events
is an empty list. The schema version is `1`.

### 009 — LangGraph skeleton

```bash
.venv/bin/python -m pytest tests/test_graph.py -v
```

Live demo — graph compiles and runs end-to-end:

```bash
.venv/bin/python -c "
from cloudpilot.graph.graph import create_graph
g = create_graph()
final = g.invoke({'request': 'test'})
print('status:', final['status'])  # → COMPLETED
print('event count:', len(final['events']))  # → 11 (one per status)
print('status sequence:', [e.status for e in final['events']])
"
```

Expected: `status` is `COMPLETED`, event count is `11` (one per
`DeploymentStatus` member), and events trace the full state machine.

### 010 — API layer

```bash
.venv/bin/python -m pytest tests/ -k 'not test_cli' -v
```

Live demo — health and 404:

```bash
.venv/bin/python -c "
from cloudpilot.api.app import create_app
from fastapi.testclient import TestClient
app = create_app()
client = TestClient(app)
print('health:', client.get('/health').json())  # → {'status': 'ok'}
print('404:', client.get('/unknown').status_code)  # → 404
"
```

Expected: `/health` returns `{"status": "ok"}`; unknown routes return `404`.

### 011 — Graph persistence

```bash
.venv/bin/python -m pytest tests/test_persistence.py -v
```

Live demo — park at approval gate and resume:

```bash
.venv/bin/python -c "
from cloudpilot.core.config import Settings
from cloudpilot.graph.persistence import create_gated_graph
settings = Settings(_env_file=None)
g = create_gated_graph(settings=settings)
config = {'configurable': {'thread_id': 'demo'}}
g.invoke({'request': 'test'}, config)
state = g.get_state(config)
print('parked at:', state.values['status'])  # → WAITING_FOR_APPROVAL
print('next node:', state.next)  # → ('DEPLOYING',)
g.invoke(None, config)  # resume
print('completed:', g.get_state(config).values['status'])  # → COMPLETED
"
```

Expected: the run parks at `WAITING_FOR_APPROVAL` with `next == ('DEPLOYING',)`;
resuming completes the run with no duplicated events.

### 012 — Checkpoint storage (SQLite)

```bash
.venv/bin/python -m pytest tests/test_checkpoints.py -v
```

Live demo — restart round-trip (simulates process restart):

```bash
.venv/bin/python -c "
from pathlib import Path
from tempfile import TemporaryDirectory
from cloudpilot.core.config import Settings
from cloudpilot.graph.persistence import create_checkpointer, create_gated_graph
with TemporaryDirectory() as tmp:
    path = Path(tmp) / 'cp.db'
    settings = Settings(checkpoint_backend='sqlite', checkpoint_path=path, _env_file=None)
    g1 = create_gated_graph(settings=settings)
    config = {'configurable': {'thread_id': 'restart'}}
    g1.invoke({'request': 'test'}, config)
    del g1  # close connection to flush
    # New instance, same file
    g2 = create_gated_graph(settings=settings)
    state = g2.get_state(config)
    print('survived restart:', state.values['status'])  # → WAITING_FOR_APPROVAL
"
```

Expected: the run state survives process restart and can be resumed from the
same file.

### 013 — Graph visualization

```bash
.venv/bin/python -m pytest tests/test_graph_visualize.py -v
```

Live demo — mermaid output:

```bash
.venv/bin/python -c "
from cloudpilot.core.config import Settings
from cloudpilot.graph.persistence import create_gated_graph
from cloudpilot.graph.visualize import mermaid
settings = Settings(_env_file=None)
g = create_gated_graph(settings=settings)
print(mermaid(g))  # → Mermaid flowchart with all nodes
" > graph.mmd

# CLI script
python scripts/visualize_graph.py --format mermaid --output graph.mmd
```

Expected: mermaid output contains all 11 status nodes, `__start__`, `__end__`,
and the `__interrupt = before` marker on `DEPLOYING`.


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
