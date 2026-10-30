# syntax=docker/dockerfile:1
# CloudPilot container. Multi-stage so uv and build tooling never reach the
# runtime image; the runtime user is non-root and the image contains no AWS
# credentials — operators supply credentials at runtime (env or mounted
# ~/.aws); see src/cloudpilot/core/aws.py.

FROM python:3.12-slim AS builder

# uv copied from its release image rather than installed via pip.
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /usr/local/bin/uv

WORKDIR /app
# Copy-mode linking: no network hardlinks, deterministic layer caching.
ENV UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never

# Dependency layer first: unchanged source deps reuse this cached layer.
COPY pyproject.toml README.md ./
COPY src ./src
# DEVIATION (recorded in the task): dependencies resolve unpinned here —
# AGENTS.md forbids committing a lockfile or == pins until the pinning
# follow-up task. Rebuild the image to pick up dependency updates.
RUN uv venv --python 3.12 /app/.venv \
    && uv pip install --python /app/.venv/bin/python --no-cache .

FROM python:3.12-slim

# Fixed-UID non-root runtime user with a home dir (some libs write ~/.cache).
RUN groupadd --gid 1000 cloudpilot \
    && useradd --uid 1000 --gid cloudpilot --create-home cloudpilot

WORKDIR /app
COPY --from=builder --chown=cloudpilot:cloudpilot /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" HOME=/home/cloudpilot

USER cloudpilot
EXPOSE 8000

# python, not curl: slim images ship no curl — a classic silent-failure.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["uvicorn", "cloudpilot.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
