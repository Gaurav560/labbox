"""Lostdesk, chapter 7: response models. A report holds a phone number; the public must never see it."""
from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()


class Line(str, Enum):
    red = "red"
    blue = "blue"
    green = "green"


class ReportIn(BaseModel):
    """What a passenger sends. The contact is for staff only."""

    title: str = Field(min_length=3, max_length=60)
    line: Line
    station: str
    contact: str = Field(min_length=6, max_length=40)
    details: str | None = None


class ReportPublic(BaseModel):
    """What anyone may see about a report: no contact."""

    id: int
    title: str
    line: Line
    station: str
    details: str | None = None
    status: str


REPORTS: dict[int, dict] = {
    1: {"id": 1, "title": "grey laptop bag", "line": "red", "station": "Tech Park", "contact": "98200 11111",
        "details": "a tiger sticker on the front", "status": "open"},
    2: {"id": 2, "title": "child's blue water bottle", "line": "green", "station": "Airport", "contact": "98200 22222",
        "details": None, "status": "open"},
}


@app.post("/reports")
def report_lost(report: ReportIn) -> ReportPublic:
    new_id = max(REPORTS, default=0) + 1
    REPORTS[new_id] = {"id": new_id, **report.model_dump(mode="json"), "status": "open"}
    return REPORTS[new_id]


@app.get("/reports")
def list_reports() -> list[ReportPublic]:
    return list(REPORTS.values())


@app.get("/reports/{report_id}")
def get_report(report_id: int) -> ReportPublic:
    if report_id not in REPORTS:
        raise HTTPException(status_code=404, detail="No report with that id")
    return REPORTS[report_id]
