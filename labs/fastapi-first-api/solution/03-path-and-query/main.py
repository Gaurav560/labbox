"""Lostdesk, chapter 3: path parameters and query parameters."""
from enum import Enum

from fastapi import FastAPI, HTTPException

app = FastAPI()


class Line(str, Enum):
    """The three metro lines. Only these values are allowed in a path."""

    red = "red"
    blue = "blue"
    green = "green"


FOUND = {
    1: {"id": 1, "title": "black umbrella", "category": "umbrella", "line": "red", "station": "Riverside"},
    2: {"id": 2, "title": "blue school bag", "category": "bag", "line": "blue", "station": "Old Market"},
    3: {"id": 3, "title": "silver phone", "category": "phone", "line": "red", "station": "Tech Park"},
    4: {"id": 4, "title": "bunch of keys", "category": "keys", "line": "green", "station": "Riverside"},
    5: {"id": 5, "title": "brown leather wallet", "category": "wallet", "line": "blue", "station": "University"},
    6: {"id": 6, "title": "green umbrella", "category": "umbrella", "line": "green", "station": "Airport"},
}


@app.get("/items")
def list_items(q: str | None = None, category: str | None = None, limit: int = 10):
    items = list(FOUND.values())
    if q:
        items = [item for item in items if q.lower() in item["title"].lower()]
    if category:
        items = [item for item in items if item["category"] == category]
    return {"items": items[:limit]}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    return FOUND[item_id]


@app.get("/lines/{line}/items")
def items_on_line(line: Line):
    return {"line": line, "items": [item for item in FOUND.values() if item["line"] == line.value]}
