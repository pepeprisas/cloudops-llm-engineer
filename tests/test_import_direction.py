"""Enforce the import-direction contract documented in ``README.md``.

Dependencies between ``cloudpilot`` subpackages flow one way: ``models/`` is
a leaf, ``core/`` never imports the workflow packages, ``api/`` is transport
only, and so on. The rules are mirrored from the README table in
``ALLOWED_IMPORTS`` below; when one changes, change both.

The check is an AST walk rather than a runtime import test so violations are
found without importing (and executing) every module, and without adding a
dependency such as import-linter. Only intra-``cloudpilot`` edges are in
scope; third-party imports are ignored, and imports within a single
subpackage are always allowed.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "src" / "cloudpilot"
TOP_LEVEL = "cloudpilot"

# Source subpackage -> subpackages it may import. A subpackage missing from
# this table fails ``test_every_subpackage_has_an_allow_rule``.
ALLOWED_IMPORTS: dict[str, set[str]] = {
    "models": set(),
    "core": {"models"},
    "mcp": {"core", "models"},
    "agents": {"core", "models", "mcp"},
    "graph": {"agents", "core", "mcp", "models"},
    "api": {"core", "graph", "models"},
}


def _subpackage_of(module: str) -> str | None:
    """Return the top-level subpackage ``module`` belongs to, if any."""
    parts = module.split(".")
    if len(parts) < 2 or parts[0] != TOP_LEVEL:
        return None
    return parts[1]


def _imported_subpackages(statement: ast.stmt, package: list[str]) -> Iterable[str]:
    """Yield every ``cloudpilot.<subpackage>`` a statement imports."""
    if isinstance(statement, ast.Import):
        for alias in statement.names:
            subpackage = _subpackage_of(alias.name)
            if subpackage is not None:
                yield subpackage
        return

    assert isinstance(statement, ast.ImportFrom)
    if statement.level:
        # Relative import: level 1 is the current package, 2 one level up.
        if statement.level > len(package):
            return
        base = package[: len(package) - (statement.level - 1)]
        module = ".".join([*base, statement.module or ""])
    else:
        module = statement.module or ""

    subpackage = _subpackage_of(module)
    if subpackage is not None:
        yield subpackage
        return

    # `from cloudpilot import <subpackage>` names the subpackage directly.
    if module == TOP_LEVEL:
        for alias in statement.names:
            if alias.name in ALLOWED_IMPORTS:
                yield alias.name


def _violations() -> list[str]:
    found: list[str] = []
    for path in sorted(PACKAGE_ROOT.rglob("*.py")):
        relative = path.relative_to(PACKAGE_ROOT)
        package = [TOP_LEVEL, *relative.parts[:-1]]
        source = _subpackage_of(".".join(package))
        if source is None:
            continue  # src/cloudpilot/__init__.py itself has no subpackage
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            for target in _imported_subpackages(node, package):
                if target == source or target in ALLOWED_IMPORTS[source]:
                    continue
                found.append(f"{relative}:{node.lineno}: {source} imports {target}")
    return found


@pytest.mark.unit
def test_every_subpackage_has_an_allow_rule() -> None:
    # A new subpackage must get an explicit rule instead of silently evading
    # the direction check.
    on_disk = {
        entry.name
        for entry in PACKAGE_ROOT.iterdir()
        if entry.is_dir() and (entry / "__init__.py").exists()
    }
    assert on_disk == set(ALLOWED_IMPORTS), "subpackages and ALLOWED_IMPORTS disagree"


@pytest.mark.unit
def test_imports_follow_the_documented_direction() -> None:
    violations = _violations()
    assert violations == [], "import-direction violations:\n" + "\n".join(violations)
