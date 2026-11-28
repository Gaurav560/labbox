"""Lostdesk, chapter 14: the app, assembled from its parts. Start it with: fastapi dev app/main.py"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import create_db_and_tables
from .routers import items, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Lostdesk",
    version="1.0.0",
    summary="The lost-property API of a city metro.",
    lifespan=lifespan,
)

app.include_router(items.router)
app.include_router(reports.router)


@app.get("/", tags=["status"])
def home():
    return {"message": "Lostdesk is open. Try /items"}
