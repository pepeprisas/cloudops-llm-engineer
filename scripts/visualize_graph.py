#!/usr/bin/env python3
"""CLI to visualize the deployment workflow graph.

Outputs a Mermaid diagram by default; PNG rendering is optional and requires
pygraphviz (warnings if unavailable).

Usage:
    python scripts/visualize_graph.py [--format mermaid|png] --output PATH

Examples:
    # Mermaid to stdout (default)
    python scripts/visualize_graph.py

    # Mermaid to file
    python scripts/visualize_graph.py --format mermaid --output graph.mmd

    # PNG (requires pygraphviz)
    python scripts/visualize_graph.py --format png --output deployments.png
"""

from __future__ import annotations

import argparse
import sys

from cloudpilot.core.config import Settings
from cloudpilot.graph.persistence import create_gated_graph
from cloudpilot.graph.visualize import mermaid, mermaid_to_file, png


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render the CloudPilot deployment graph to Mermaid or PNG.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--format",
        choices=["mermaid", "png"],
        default="mermaid",
        help="Output format (default: mermaid)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path; if omitted and format=mermaid, prints to stdout",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress warnings (e.g. missing pygraphviz for PNG)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    settings = Settings(_env_file=None)
    graph = create_gated_graph(settings=settings)

    if args.format == "mermaid":
        if args.output:
            mermaid_to_file(graph, args.output)
            print(f"Mermaid written to {args.output}", file=sys.stderr)
        else:
            print(mermaid(graph))
    elif args.format == "png":
        if args.quiet:
            import warnings

            warnings.filterwarnings("ignore", category=UserWarning)
        success = png(graph, args.output or "graph.png")
        if success:
            print(f"PNG written to {args.output or 'graph.png'}", file=sys.stderr)
        else:
            print("PNG rendering skipped (pygraphviz not installed)", file=sys.stderr)
            return 1
    else:
        print(f"Unknown format: {args.format}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
