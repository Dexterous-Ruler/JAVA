from __future__ import annotations

from fastapi import FastAPI

from .db import init_db
from .routers import agencies, branding, clients, context, domains, invitations, users


def create_app() -> FastAPI:
    app = FastAPI(title="Agency White Label Backend", version="0.1.0")

    @app.on_event("startup")
    def _startup() -> None:  # pragma: no cover - executed during runtime
        init_db()

    app.include_router(users.router)
    app.include_router(agencies.router)
    app.include_router(clients.router)
    app.include_router(branding.router)
    app.include_router(domains.router)
    app.include_router(invitations.router)
    app.include_router(context.router)

    return app


app = create_app()
