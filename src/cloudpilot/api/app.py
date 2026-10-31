"""FastAPI application factory wiring the LangGraph gate operations.

Task 006 delivers only what the container health check needs: an app
factory with a single unauthenticated ``GET /health``. Task 010 builds the
real API layer (routes, the LangGraph entry point, approvals transport) on
this factory.

The health endpoint reports status only — no configuration, version
detail, or resource identifiers. Other endpoints are wired to the
LangGraph state machine in :mod:`cloudpilot.graph.persistence`.
"""

from fastapi import FastAPI

from cloudpilot.api.routes import router as routes_router


def create_app() -> FastAPI:
    """Build the CloudPilot application."""
    app = FastAPI(title="CloudPilot", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    # Routes are mounted separately so they can import without circular
    # dependencies (persistence needs settings; settings are a singleton).
    app.include_router(routes_router, prefix="/api/v1")

    return app
