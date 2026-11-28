"""Lostdesk, chapter 19: middleware, CORS and settings from the environment."""
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Every setting can be changed with an environment variable, like LOSTDESK_MAX_PHOTO_MB=5."""

    model_config = SettingsConfigDict(env_prefix="LOSTDESK_")

    app_name: str = "Lostdesk"
    max_photo_mb: int = 2
    allowed_origin: str = "https://screens.metro.example"


settings = Settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origin],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{(time.perf_counter() - start) * 1000:.2f} ms"
    return response


@app.get("/info")
def info():
    return {"app_name": settings.app_name, "max_photo_mb": settings.max_photo_mb}


@app.get("/items")
def list_items():
    return {"items": [{"id": 1, "title": "black umbrella"}]}
