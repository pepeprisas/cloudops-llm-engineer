"""Minimal FastAPI application.

Task 006 delivers only what the container health check needs: an app
factory with a single unauthenticated ``GET /health``. Task 010 builds the
real API layer (routes, the LangGraph entry point, approvals transport) on
this factory.

The health endpoint reports status only — no configuration, version
detail, or resource identifiers.
"""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Build the CloudPilot application."""
    app = FastAPI(title="CloudPilot", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
