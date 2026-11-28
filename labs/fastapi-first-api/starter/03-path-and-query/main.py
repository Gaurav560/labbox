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
def list_items():
    # TODO (task search): add three optional query parameters: q (a part of the title, any capitals), category,
    # and limit (at most this many items, 10 when not given).
    return {"items": list(FOUND.values())}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    return FOUND[item_id]


# TODO (task by_line): GET /lines/{line}/items gives back {"line": ..., "items": [...]}, the items found on that line.
# Use the Line enum as the parameter's type, so only red, blue and green are allowed.
