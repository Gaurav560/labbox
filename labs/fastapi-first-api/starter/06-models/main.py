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


# TODO (task nested_location): a model Location with line (a Line) and station (2 to 40 characters).


class FoundItemIn(BaseModel):
    # TODO (task item_fields): title 3 to 60 characters; add found_on, a date, and tags, a list of up to 5 texts
    # (an empty list when not sent).
    title: str
    category: Category
    # TODO (task nested_location): replace line and station with location: Location.
    line: Line
    station: str


FOUND: dict[int, dict] = {
    1: {"id": 1, "title": "black umbrella", "category": "umbrella", "line": "red", "station": "Riverside"},
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
