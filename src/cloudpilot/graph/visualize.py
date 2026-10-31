"""Graph visualization: mermaid and optional PNG rendering.

Exports functions to render the compiled LangGraph to:

- Mermaid text (always available; suitable for embedding in markdown/docs)
- PNG file (optional; requires pygraphviz, otherwise skipped with a warning)

The rendered diagram reflects the current graph structure: nodes derived from
:class:`~cloudpilot.graph.state.DeploymentStatus` in declaration order, edges
following the state machine (linear by default, conditional routing is Phase 6).

All rendering is read-only and performs no external I/O beyond the target file.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any


def mermaid(graph: Any) -> str:
    """Return the compiled graph as Mermaid syntax.

    The output is a valid Mermaid flowchart diagram that renders nodes for
    each :class:`~cloudpilot.graph.state.DeploymentStatus` and edges for
    the transitions between them.

    To display or embed, render with a Mermaid renderer (e.g. GitHub,
    mermaid-cli, or any markdown viewer that supports Mermaid).

    Args:
        graph: A compiled LangGraph compiled via :func:`cloudpilot.graph.graph.create_graph`
            or :func:`cloudpilot.graph.persistence.create_gated_graph`.

    Returns:
        Mermaid flowchart text with graph TD (top-down) orientation.
    """
    pregel_graph = graph.get_graph()
    text: str = pregel_graph.draw_mermaid()
    return text


def png(graph: Any, output_path: Path | str) -> bool:
    """Render the compiled graph to a PNG file.

    This is a convenience wrapper around :meth:`langchain_core.runnables.graph.Graph.draw_png`.

    Args:
        graph: A compiled LangGraph.
        output_path: Target file path (``.png`` extension recommended).

    Returns:
        ``True`` if rendering succeeded, ``False`` if required dependencies
        (pygraphviz) are unavailable — in which case a warning is logged
        and no file is written.
    """
    try:
        import pygraphviz  # type: ignore[import-not-found]

        _ = pygraphviz.__name__  # Use to suppress unused-import
    except ImportError:
        warnings.warn(
            "PNG rendering requires pygraphviz. Install with: pip install pygraphviz",
            stacklevel=2,
        )
        return False

    pregel_graph = graph.get_graph()
    if not isinstance(output_path, Path):
        output_path = Path(output_path)

    pregel_graph.draw_png(str(output_path))
    return True


def mermaid_to_file(graph: Any, output_path: Path | str) -> None:
    """Write the compiled graph as a Mermaid diagram to a file.

    Args:
        graph: A compiled LangGraph.
        output_path: Target file path (``.mmd`` or ``.md`` recommended).

    Example:
        >>> from cloudpilot.graph.persistence import create_gated_graph
        >>> from cloudpilot.core.config import Settings
        >>> from pathlib import Path
        >>> settings = Settings(_env_file=None)
        >>> graph = create_gated_graph(settings=settings)
        >>> mermaid_to_file(graph, Path("graph.mmd"))
    """
    pregel_graph = graph.get_graph()
    mermaid_text = pregel_graph.draw_mermaid()
    if not isinstance(output_path, Path):
        output_path = Path(output_path)
    output_path.write_text(mermaid_text, encoding="utf-8")
