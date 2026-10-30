"""Scaffold tests: the installed package and its subpackages must import."""

import importlib

import pytest

SUBPACKAGES = ["agents", "api", "core", "graph", "mcp", "models"]


@pytest.mark.unit
def test_top_level_package_imports() -> None:
    assert importlib.import_module("cloudpilot")


@pytest.mark.unit
@pytest.mark.parametrize("subpackage", SUBPACKAGES)
def test_subpackage_imports_and_is_a_package(subpackage: str) -> None:
    # Asserting __path__ rather than mere import success means a subpackage
    # that degrades to a stray module, or is deleted, fails here.
    module = importlib.import_module(f"cloudpilot.{subpackage}")
    assert hasattr(module, "__path__")
