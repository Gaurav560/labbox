"""Lostdesk, chapter 19: middleware, CORS and settings from the environment."""
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict

# TODO (task settings_env): replace these three constants with a Settings class (BaseSettings) whose fields have these
# defaults and can be changed with environment variables starting LOSTDESK_ (LOSTDESK_MAX_PHOTO_MB=5, ...). Create
# settings = Settings(), and use settings.app_name, settings.max_photo_mb and settings.allowed_origin below.
APP_NAME = "Lostdesk"
MAX_PHOTO_MB = 2
ALLOWED_ORIGIN = "https://screens.metro.example"

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# TODO (task timing_header): an HTTP middleware that measures how long each request takes and adds the header
# X-Process-Time to every response, like "0.42 ms".


@app.get("/info")
def info():
    return {"app_name": APP_NAME, "max_photo_mb": MAX_PHOTO_MB}


@app.get("/items")
def list_items():
    return {"items": [{"id": 1, "title": "black umbrella"}]}
