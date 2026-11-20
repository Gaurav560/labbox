import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import text

from . import containers, llm_gateway, metrics, observability, preview, shared
from .config import get_settings
from .db import init_db
from .content import init_content
from .labs import init_labs
from .reaper import reaper_loop
from .routers import (
    ai_routes,
    auth_routes,
    check_routes,
    engagement_routes,
    file_routes,
    lab_routes,
    preview_routes,
    progress_routes,
    terminal_routes,
)

observability.setup_logging()  # LOG_FORMAT=json for one JSON object a line
observability.setup_sentry()  # only with SENTRY_DSN; otherwise nothing is sent anywhere
log = logging.getLogger("labbox")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    init_labs(settings.LABS_DIR)  # raises (and stops startup) if any lab is invalid
    init_content(settings.LABS_DIR.parent)  # skill maps, drills, onboarding next to labs/; same rule
    init_db()
    settings.VOLUMES_DIR.mkdir(parents=True, exist_ok=True)
    settings.CHECKS_DIR.mkdir(parents=True, exist_ok=True)
    reaper = asyncio.create_task(reaper_loop())
    gateway = asyncio.create_task(llm_gateway.serve()) if settings.LLM_GATEWAY_ENABLED else None
    yield
    reaper.cancel()
    if gateway:
        gateway.cancel()
    await preview.close_client()


app = FastAPI(title="LabBox by Telusko", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(observability.RequestMiddleware)  # request ids, metrics, slow and failed requests
app.include_router(auth_routes.router)
app.include_router(lab_routes.router)
app.include_router(lab_routes.public_router)
app.include_router(file_routes.router)
app.include_router(check_routes.router)
app.include_router(terminal_routes.router)
app.include_router(progress_routes.router)
app.include_router(engagement_routes.router)
app.include_router(preview_routes.router)
app.include_router(ai_routes.router)


class Health(BaseModel):
    ok: bool
    docker: bool
    database: bool = True
    shared_state: bool = True  # Redis (or memory, which is always fine)


def _database_ok() -> bool:
    try:
        from .db import engine

        with engine.connect() as c:
            c.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@app.get("/api/health", response_model=Health)
async def health() -> Health:
    docker, database, state = await asyncio.gather(
        asyncio.to_thread(containers.docker_ok), asyncio.to_thread(_database_ok), asyncio.to_thread(shared.ping)
    )
    # ok keeps its old meaning (the backend answers); each part reports on its own.
    return Health(ok=True, docker=docker, database=database, shared_state=state)


@app.get("/metrics", include_in_schema=False, response_class=PlainTextResponse)
async def prometheus_metrics(request: Request) -> PlainTextResponse:
    """Prometheus' text format. Only for this machine or a request with METRICS_TOKEN (Phase H6)."""
    if not metrics.allowed(request.client.host if request.client else None, request.headers.get("authorization")):
        raise HTTPException(404)
    body = await asyncio.to_thread(metrics.render)
    return PlainTextResponse(body, media_type="text/plain; version=0.0.4")
