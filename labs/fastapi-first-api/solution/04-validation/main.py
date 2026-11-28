"""Lostdesk, chapter 4: validating parameters with Query and Path."""
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query

app = FastAPI()

FOUND = {
    1: {"id": 1, "title": "black umbrella", "category": "umbrella", "line": "red", "station": "Riverside"},
    2: {"id": 2, "title": "blue school bag", "category": "bag", "line": "blue", "station": "Old Market"},
    3: {"id": 3, "title": "silver phone", "category": "phone", "line": "red", "station": "Tech Park"},
    4: {"id": 4, "title": "bunch of keys", "category": "keys", "line": "green", "station": "Riverside"},
    5: {"id": 5, "title": "brown leather wallet", "category": "wallet", "line": "blue", "station": "University"},
    6: {"id": 6, "title": "green umbrella", "category": "umbrella", "line": "green", "station": "Airport"},
}


@app.get("/items")
def list_items(
    q: Annotated[str | None, Query(min_length=3, max_length=40)] = None,
    category: str | None = None,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    items = list(FOUND.values())
    if q:
        items = [item for item in items if q.lower() in item["title"].lower()]
    if category:
        items = [item for item in items if item["category"] == category]
    return {"items": items[offset : offset + limit]}


@app.get("/items/{item_id}")
def get_item(item_id: Annotated[int, Path(ge=1)]):
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    return FOUND[item_id]
