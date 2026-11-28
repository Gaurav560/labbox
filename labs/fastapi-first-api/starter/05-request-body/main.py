"""Lostdesk, chapter 5: request bodies. Staff log what they find; passengers report what they lost."""
from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Line(str, Enum):
    red = "red"
    blue = "blue"
    green = "green"


class FoundItemIn(BaseModel):
    """What a member of staff sends when they log something found on a train."""

    title: str
    category: str
    line: Line
    station: str


class LostReport(BaseModel):
    """What a passenger sends when they have lost something."""

    title: str
    line: Line
    station: str
    contact: str
    details: str | None = None


FOUND = {
    1: {"id": 1, "title": "black umbrella", "category": "umbrella", "line": "red", "station": "Riverside"},
    2: {"id": 2, "title": "blue school bag", "category": "bag", "line": "blue", "station": "Old Market"},
    3: {"id": 3, "title": "silver phone", "category": "phone", "line": "red", "station": "Tech Park"},
}
REPORTS: list[dict] = []


@app.get("/items")
def list_items():
    return {"items": list(FOUND.values())}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    return FOUND[item_id]


# TODO (task found_item): POST /items takes a FoundItemIn as its body, stores it in FOUND under the next id
# (one more than the biggest id so far) and gives back the stored item, id included.


# TODO (task report_lost): POST /reports takes a LostReport as its body, adds it to REPORTS with an id
# (1 for the first report, 2 for the next, ...) and gives back what was stored.


@app.get("/reports")
def list_reports():
    return {"reports": REPORTS}
