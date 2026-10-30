# Developer entry points for CloudPilot. The uv-managed virtualenv holds the
# toolchain; targets call its binaries directly so `make` and manual commands
# always run the same versions.
#
# `make install` must run once before anything else (including
# `pre-commit install`), because the hooks call .venv binaries.

VENV := .venv
PYTHON := $(VENV)/bin/python

.PHONY: install lint format typecheck test

$(PYTHON):
	uv venv --python 3.12 $(VENV)

# Deliberately `uv pip install` rather than `uv sync`: it reads no lockfile,
# matching the project rule that uv.lock is not committed yet (AGENTS.md).
install: $(PYTHON)
	uv pip install -e . --group dev --python $(PYTHON)

lint:
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .

format:
	$(VENV)/bin/ruff format .

typecheck:
	$(VENV)/bin/mypy

test:
	$(PYTHON) -m pytest -q
