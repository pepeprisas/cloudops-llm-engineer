# Task 013 - Graph Visualization

## Goal

Render the compiled LangGraph to a mermaid and/or PNG diagram for documentation and debugging, plus a script to regenerate it on demand.

## Inputs

The compiled graph from Task 009.

## Outputs

A visualization module and a CLI script that emit a mermaid/PNG diagram of the graph.

## Dependencies

Task 009

## Acceptance Criteria

- A function renders the compiled graph to mermaid text and/or a PNG file
- `scripts/visualize_graph.py` runs and writes the diagram to a target path
- Output reflects all nodes and edges of the current graph
- Script has a clear CLI (output path/format arguments)
- Rendering is read-only and performs no shell/AWS execution
- Unit tests pass (mermaid generation; PNG rendering skipped if deps unavailable)

## Out of Scope

Live/interactive graph dashboards and embedding diagrams into a docs site.

## Deliverables

src/cloudpilot/graph/visualize.py
scripts/visualize_graph.py
