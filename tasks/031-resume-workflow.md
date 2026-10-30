# Task 031 - Resume Workflow

## Goal

Implement the ability to resume a paused run from its persisted checkpoint after a human approval. This loads the checkpoint and continues the graph from where it was interrupted.

## Inputs

Persisted checkpoint for a paused run (Task 012); approval signal from the approval workflow (Task 029).

## Outputs

A resumed, running graph execution continued from the loaded checkpoint.

## Dependencies

Task 029
Task 012

## Acceptance Criteria

- Loads a paused run's checkpoint and resumes graph execution from it
- Only resumes runs that have a recorded approval
- Resumption does not re-run already-completed nodes or duplicate side effects
- The resume action is recorded to the audit trail (who/what/when)
- No direct shell execution; any terraform work happens via the Terraform MCP (Task 019)
- Unit tests pass

## Out of Scope

Does not implement the reject or cancel paths (Tasks 030, 032); does not perform recovery of a corrupted/interrupted apply (Task 037).

## Deliverables

src/cloudpilot/graph/resume.py
tests/test_resume.py
