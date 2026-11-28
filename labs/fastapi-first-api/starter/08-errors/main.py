"""Lostdesk, chapter 8: status codes and errors. 201 for new things, 409 when an item is already claimed."""
from enum import Enum

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


class Line(str, Enum):
    red = "red"
    blue = "blue"
    green = "green"


class FoundItemIn(BaseModel):
    title: str
    line: Line
    station: str


class Claim(BaseModel):
    """A passenger's report that matches a found item."""

    report_id: int


class AlreadyClaimed(Exception):
    """Raised when someone tries to claim an item that already has an owner."""

    def __init__(self, item_id: int, report_id: int):
        self.item_id, self.report_id = item_id, report_id


# TODO (task claim_conflict): an exception handler for AlreadyClaimed that answers 409 with
# {"detail": "Item <id> is already claimed", "claimed_by_report": <report id>}.


FOUND: dict[int, dict] = {
    1: {"id": 1, "title": "black umbrella", "line": "red", "station": "Riverside", "claimed_by": None},
    2: {"id": 2, "title": "blue school bag", "line": "blue", "station": "Old Market", "claimed_by": None},
    3: {"id": 3, "title": "silver phone", "line": "red", "station": "Tech Park", "claimed_by": 7},
}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    return FOUND[item_id]


# TODO (task created_201): a new item is created, so the answer's status should be 201, not 200.
@app.post("/items")
def log_found_item(item: FoundItemIn):
    new_id = max(FOUND) + 1
    FOUND[new_id] = {"id": new_id, **item.model_dump(mode="json"), "claimed_by": None}
    return FOUND[new_id]


@app.post("/items/{item_id}/claim")
def claim_item(item_id: int, claim: Claim):
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    item = FOUND[item_id]
    # TODO (task claim_conflict): an item that already has claimed_by must not be claimed again: raise AlreadyClaimed.
    item["claimed_by"] = claim.report_id
    return item
