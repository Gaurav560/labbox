"""Lostdesk, chapter 6: richer models. Field rules, a nested location, dates and lists."""
from datetime import date
from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()


class Line(str, Enum):
    red = "red"
    blue = "blue"
    green = "green"


class Category(str, Enum):
    bag = "bag"
    clothing = "clothing"
    keys = "keys"
    phone = "phone"
    umbrella = "umbrella"
    wallet = "wallet"
    other = "other"


class Location(BaseModel):
    """Where on the network something was found."""

    line: Line
    station: str = Field(min_length=2, max_length=40)


class FoundItemIn(BaseModel):
    title: str = Field(min_length=3, max_length=60, examples=["black umbrella"])
    category: Category
    location: Location
    found_on: date
    tags: list[str] = Field(default=[], max_length=5)


FOUND: dict[int, dict] = {
    1: {"id": 1, "title": "black umbrella", "category": "umbrella", "location": {"line": "red", "station": "Riverside"},
        "found_on": "2026-11-26", "tags": ["long handle"]},
}


@app.get("/items")
def list_items():
    return {"items": list(FOUND.values())}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    return FOUND[item_id]


@app.post("/items")
def log_found_item(item: FoundItemIn):
    new_id = max(FOUND) + 1
    FOUND[new_id] = {"id": new_id, **item.model_dump(mode="json")}
    return FOUND[new_id]
