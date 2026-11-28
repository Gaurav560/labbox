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


@app.post("/items")
def log_found_item(item: FoundItemIn):
    new_id = max(FOUND) + 1
    FOUND[new_id] = {"id": new_id, **item.model_dump(mode="json")}
    return FOUND[new_id]


@app.post("/reports")
def report_lost(report: LostReport):
    stored = {"id": len(REPORTS) + 1, **report.model_dump(mode="json")}
    REPORTS.append(stored)
    return stored


@app.get("/reports")
def list_reports():
    return {"reports": REPORTS}
