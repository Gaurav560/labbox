"""Lostdesk, chapter 11: dependencies. Paging and the desk key, written once and used by many routes."""
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response, status
from pydantic import BaseModel

app = FastAPI()

DESK_KEYS = {"riverside-desk-7": "Riverside", "airport-desk-2": "Airport"}


# TODO (task pagination_dep): a dependency paginate that reads offset (0 or more, default 0) and limit (1 to 20,
# default 10) from the query and gives them back together; use it in both GET routes.


# TODO (task desk_dep): a dependency require_desk that reads the X-Desk-Key header and answers 401 unless the key is in
# DESK_KEYS; it gives back the desk's station. Use it on POST /items (to fill logged_at) and on DELETE /items/{item_id}.


class FoundItemIn(BaseModel):
    title: str


FOUND: dict[int, dict] = {i: {"id": i, "title": t, "logged_at": "Riverside"} for i, t in enumerate(
    ["black umbrella", "blue school bag", "silver phone", "bunch of keys", "brown leather wallet", "green umbrella"], 1)}
REPORTS: list[dict] = [{"id": i, "title": t} for i, t in enumerate(
    ["grey laptop bag", "child's water bottle", "red scarf", "reading glasses"], 1)]


@app.get("/items")
def list_items(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
):
    items = list(FOUND.values())
    return {"items": items[offset : offset + limit]}


@app.get("/reports")
def list_reports():
    return {"reports": REPORTS}


@app.post("/items", status_code=status.HTTP_201_CREATED)
def log_found_item(item: FoundItemIn, x_desk_key: Annotated[str | None, Header()] = None):
    if x_desk_key not in DESK_KEYS:
        raise HTTPException(status_code=401, detail="Only staff at a desk can do this")
    new_id = max(FOUND) + 1
    FOUND[new_id] = {"id": new_id, "title": item.title, "logged_at": DESK_KEYS[x_desk_key]}
    return FOUND[new_id]


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    del FOUND[item_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
