"""Lostdesk, chapter 2: the same API, looked at as HTTP requests and responses."""
from fastapi import FastAPI, HTTPException

app = FastAPI()

FOUND = {
    1: {"id": 1, "title": "black umbrella", "station": "Riverside"},
    2: {"id": 2, "title": "blue school bag", "station": "Old Market"},
    3: {"id": 3, "title": "silver phone", "station": "Tech Park"},
    4: {"id": 4, "title": "bunch of keys", "station": "Riverside"},
}


@app.get("/")
def home():
    return {"message": "Lostdesk is open. Try /items"}


@app.get("/items")
def list_items():
    return {"items": list(FOUND.values())}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    return FOUND[item_id]


# TODO (task health): GET /health gives back {"status": "ok", "items": <how many found items there are>}.


# TODO (task stations): GET /stations gives back {"stations": [...]}, every station that has a found item,
# each once, A to Z.
