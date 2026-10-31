"""Unit tests for graph visualization: mermaid and optional PNG.

Acceptance criteria (Task 013):
- Mermaid rendering includes all nodes and edges
- PNG rendering works when pygraphviz is available, skips gracefully when not
- CLI script runs and writes to target path
- Output is read-only, no shell/AWS execution
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from cloudpilot.core.config import Settings
from cloudpilot.graph.persistence import create_gated_graph
from cloudpilot.graph.state import DeploymentStatus
from cloudpilot.graph.visualize import mermaid, mermaid_to_file, png


@pytest.fixture
def graph() -> Any:
    """Compile the serving graph once per test module."""
    settings = Settings(_env_file=None)
    return create_gated_graph(settings=settings)


@pytest.mark.unit
def test_mermaid_includes_all_nodes(graph: Any) -> None:
    """Mermaid output contains every status node and terminal markers."""
    output = mermaid(graph)

    for status in DeploymentStatus:
        assert status.value in output, f"Missing node: {status.value}"
    assert "__start__" in output
    assert "__end__" in output


@pytest.mark.unit
def test_mermaid_shows_interrupt_before_deploying(graph: Any) -> None:
    """The gate is visible in the output: DEPLOYING is interrupted before."""
    output = mermaid(graph)
    assert "__interrupt = before" in output
    assert "DEPLOYING" in output


@pytest.mark.unit
def test_mermaid_to_file_writes_to_path(graph: Any, tmp_path: Path) -> None:
    """mermaid_to_file writes Mermaid text to the target path."""
    target = tmp_path / "graph.mmd"
    mermaid_to_file(graph, target)
    content = target.read_text(encoding="utf-8")
    assert "graph TD" in content
    assert "REQUEST_RECEIVED" in content
    assert "COMPLETED" in content


@pytest.mark.unit
def test_png_returns_false_without_pygraphviz(graph: Any, tmp_path: Path) -> None:
    """PNG fails gracefully when pygraphviz is unavailable."""
    with patch.dict(sys.modules, {"pygraphviz": None}):
        import importlib

        import cloudpilot.graph.visualize as viz

        # Reload the module to re-run the import block
        importlib.reload(viz)

        success = viz.png(graph, tmp_path / "graph.png")

    assert not success


# pygraphviz is optional; skip if not installed (my pygraphviz stub test)


@pytest.mark.unit
def test_png_imports_pygraphviz_when_present(graph: Any, tmp_path: Path) -> None:
    """Test that pygraphviz is attempted (when available) without actual file write."""
    try:
        import pygraphviz as pgv  # type: ignore[import-not-found]

        _ = pgv.__name__  # Use to suppress unused warning
        pytest.skip("pygraphviz installed; skip stub test")
    except ImportError:
        # If not available, test the stub behavior
        from cloudpilot.graph.visualize import png

        success = png(graph, tmp_path / "graph.png")
        assert not success


@pytest.mark.unit
def test_png_returns_true_with_pygraphviz(graph: Any, tmp_path: Path) -> None:
    """PNG succeeds when pygraphviz is available."""
    try:
        import pygraphviz

        _ = pygraphviz.__name__  # Use to suppress unused warning
    except ImportError:
        pytest.skip("pygraphviz not installed")

    success = png(graph, tmp_path / "graph.png")
    assert success
    assert (tmp_path / "graph.png").exists()


@pytest.mark.unit
def test_cli_mermaid_stdout(graph: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI prints mermaid to stdout when --output omitted."""
    from scripts.visualize_graph import main

    def mock_create() -> Any:
        return graph  # Override graph creation

    monkeypatch.setattr("cloudpilot.graph.persistence.create_gated_graph", mock_create)

    monkeypatch.setattr(sys, "argv", ["visualize_graph.py"])
    monkeypatch.setenv("CLOUDPILOT_CHECKPOINT_BACKEND", "memory")

    # Capture stdout
    from io import StringIO

    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        result = main()
    finally:
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

    assert result == 0
    assert "graph TD" in output


@pytest.mark.unit
def test_cli_mermaid_to_file(graph: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI writes mermaid to --output path."""
    from scripts.visualize_graph import main

    def mock_create() -> Any:
        return graph

    monkeypatch.setattr("cloudpilot.graph.persistence.create_gated_graph", mock_create)

    target = tmp_path / "graph.mmd"
    monkeypatch.setattr(
        sys, "argv", ["visualize_graph.py", "--format", "mermaid", "--output", str(target)]
    )

    result = main()

    assert result == 0
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "graph TD" in content


@pytest.mark.unit
def test_cli_png_handles_missing_deps(
    graph: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CLI exits 1 and warns when pygraphviz is MISSING."""
    from scripts.visualize_graph import main

    def mock_create() -> Any:
        return graph

    monkeypatch.setattr("cloudpilot.graph.persistence.create_gated_graph", mock_create)

    target = tmp_path / "graph.png"
    monkeypatch.setattr(
        sys, "argv", ["visualize_graph.py", "--format", "png", "--output", str(target)]
    )

    with patch.dict(sys.modules, {"pygraphviz": None}):
        import importlib

        import cloudpilot.graph.visualize as viz

        importlib.reload(viz)

        monkeypatch.setattr("cloudpilot.graph.visualize.png", viz.png)

        result = main()

    assert result == 1
