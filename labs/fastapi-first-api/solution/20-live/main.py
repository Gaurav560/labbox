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


@app.get("/items/feed", response_class=EventSourceResponse)
async def feed(
    since: int | None = None,
    last_event_id: Annotated[str | None, Header()] = None,
) -> AsyncIterable[ServerSentEvent]:
    if since is None:
        since = int(last_event_id) if last_event_id and last_event_id.isdigit() else 0
    for item in list(FOUND.values()):
        if item["id"] > since:
            yield ServerSentEvent(data=item, event="found", id=str(item["id"]))
