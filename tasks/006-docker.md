# Task 006 - Docker

## Goal

Containerize the CloudPilot application and provide a docker-compose setup for local development, including the app and a checkpoint database service.

## Inputs

`pyproject.toml` and package layout from Task 001.

## Outputs

A production-capable Dockerfile, a local docker-compose stack, and a `.dockerignore`.

## Dependencies

Task 001

## Acceptance Criteria

- `Dockerfile` builds the app image with pinned dependencies and a non-root runtime user
- `docker-compose.yml` runs the app plus a checkpoint database service for local dev
- `.dockerignore` excludes build artifacts, virtualenvs, and secrets/`.env`
- `docker compose up` starts the stack and the app responds to a health check
- No AWS credentials are baked into the image
- Unit tests pass

## Out of Scope

Production orchestration (Kubernetes/ECS), image registry publishing, and CI build steps.

## Deliverables

Dockerfile
docker-compose.yml
.dockerignore
