"""Lostdesk, chapter 9: changing and removing items with PUT, PATCH and DELETE."""
from enum import Enum

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

app = FastAPI()


class Line(str, Enum):
    red = "red"
    blue = "blue"
    green = "green"


class FoundItemIn(BaseModel):
    """A whole item: what POST and PUT take."""

    title: str
    line: Line
    station: str
    shelf: str


class ItemUpdate(BaseModel):
    """Part of an item: every field optional, for PATCH."""

    title: str | None = None
    line: Line | None = None
    station: str | None = None
    shelf: str | None = None


FOUND: dict[int, dict] = {
    1: {"id": 1, "title": "black umbrella", "line": "red", "station": "Riverside", "shelf": "U-03"},
    2: {"id": 2, "title": "blue school bag", "line": "blue", "station": "Old Market", "shelf": "B-11"},
    3: {"id": 3, "title": "silver phone", "line": "red", "station": "Tech Park", "shelf": "safe"},
}


def find(item_id: int) -> dict:
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    return FOUND[item_id]


@app.get("/items/{item_id}")
def get_item(item_id: int):
    return find(item_id)


@app.put("/items/{item_id}")
def replace_item(item_id: int, item: FoundItemIn):
    find(item_id)
    FOUND[item_id] = {"id": item_id, **item.model_dump(mode="json")}
    return FOUND[item_id]


# TODO (task patch_item): PATCH /items/{item_id} takes an ItemUpdate and changes only the fields that were sent.


# TODO (task delete_item): DELETE /items/{item_id} removes the item and answers 204 No Content; an unknown id gives 404.
