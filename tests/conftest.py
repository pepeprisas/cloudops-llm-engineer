"""Shared pytest fixtures and test-layout conventions for CloudPilot.

Conventions
-----------
- Test modules are named ``test_<thing>.py`` and live in ``tests/``.
- Tests are marked ``unit`` (the default) or ``integration``. Integration
  tests require external systems and must not run in the default workflow.
- Fixtures are function-scoped unless a resource's lifetime genuinely spans
  tests. Mutable fixture data is not shared between tests.
- Temporary files use pytest's built-in ``tmp_path`` rather than a custom
  fixture.
- Environment variables and global state changed by a test are restored.
- Tests do not call a live model, AWS, or the network. Deterministic fakes
  stand in, and a double must preserve the behaviour the contract depends on.

Why there are no fixtures yet
-----------------------------
Fixtures are added by the task that needs them, not in advance. A settings
override cannot be defined until Task 004 provides ``Settings``, and
inventing placeholder fixtures here would misrepresent what exists. See
``tasks/005-testing-framework.md``.
"""
