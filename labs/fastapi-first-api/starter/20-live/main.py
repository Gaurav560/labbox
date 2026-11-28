"""Lostdesk, chapter 20: live updates. Station screens follow new finds with Server-Sent Events."""
from collections.abc import AsyncIterable
from typing import Annotated

from fastapi import FastAPI, Header, status
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

app = FastAPI()


class FoundItemIn(BaseModel):
    title: str
    station: str


FOUND: dict[int, dict] = {
    1: {"id": 1, "title": "black umbrella", "station": "Riverside"},
    2: {"id": 2, "title": "blue school bag", "station": "Old Market"},
    3: {"id": 3, "title": "silver phone", "station": "Tech Park"},
}


@app.post("/items", status_code=status.HTTP_201_CREATED)
def log_found_item(item: FoundItemIn):
    new_id = max(FOUND) + 1
    FOUND[new_id] = {"id": new_id, **item.model_dump()}
    return FOUND[new_id]


# TODO (task sse_feed): GET /items/feed streams, as Server-Sent Events, every item whose id is greater than the query
# parameter since (0 when not given): response_class=EventSourceResponse, and yield one ServerSentEvent per item.


# TODO (task sse_resume): give each event the name "found" and the item's id, and when since is not given, start after
# the Last-Event-ID header, which a browser sends when it reconnects.
