import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import containers, preview
from .config import get_settings
from .db import init_db
from .content import init_content
from .labs import init_labs
from .reaper import reaper_loop
from .routers import (
    auth_routes,
    check_routes,
    engagement_routes,
    file_routes,
    lab_routes,
    preview_routes,
    progress_routes,
    terminal_routes,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
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
    yield
    reaper.cancel()
    await preview.close_client()


app = FastAPI(title="LabBox", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_routes.router)
app.include_router(lab_routes.router)
app.include_router(lab_routes.public_router)
app.include_router(file_routes.router)
app.include_router(check_routes.router)
app.include_router(terminal_routes.router)
app.include_router(progress_routes.router)
app.include_router(engagement_routes.router)
app.include_router(preview_routes.router)


class Health(BaseModel):
    ok: bool
    docker: bool


@app.get("/api/health", response_model=Health)
async def health() -> Health:
    return Health(ok=True, docker=await asyncio.to_thread(containers.docker_ok))
