"""Lostdesk, chapter 11: dependencies. Paging and the desk key, written once and used by many routes."""
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response, status
from pydantic import BaseModel

app = FastAPI()

DESK_KEYS = {"riverside-desk-7": "Riverside", "airport-desk-2": "Airport"}


class Page(BaseModel):
    """Which slice of a long list to give back."""

    offset: int
    limit: int


def paginate(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> Page:
    return Page(offset=offset, limit=limit)


PageDep = Annotated[Page, Depends(paginate)]


def require_desk(x_desk_key: Annotated[str | None, Header()] = None) -> str:
    """Gives back the desk's station, or refuses the request with 401."""
    if x_desk_key not in DESK_KEYS:
        raise HTTPException(status_code=401, detail="Only staff at a desk can do this")
    return DESK_KEYS[x_desk_key]


DeskDep = Annotated[str, Depends(require_desk)]


class FoundItemIn(BaseModel):
    title: str


FOUND: dict[int, dict] = {i: {"id": i, "title": t, "logged_at": "Riverside"} for i, t in enumerate(
    ["black umbrella", "blue school bag", "silver phone", "bunch of keys", "brown leather wallet", "green umbrella"], 1)}
REPORTS: list[dict] = [{"id": i, "title": t} for i, t in enumerate(
    ["grey laptop bag", "child's water bottle", "red scarf", "reading glasses"], 1)]


@app.get("/items")
def list_items(page: PageDep):
    items = list(FOUND.values())
    return {"items": items[page.offset : page.offset + page.limit]}


@app.get("/reports")
def list_reports(page: PageDep):
    return {"reports": REPORTS[page.offset : page.offset + page.limit]}


@app.post("/items", status_code=status.HTTP_201_CREATED)
def log_found_item(item: FoundItemIn, desk: DeskDep):
    new_id = max(FOUND) + 1
    FOUND[new_id] = {"id": new_id, "title": item.title, "logged_at": desk}
    return FOUND[new_id]


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_desk)])
def delete_item(item_id: int):
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    del FOUND[item_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
