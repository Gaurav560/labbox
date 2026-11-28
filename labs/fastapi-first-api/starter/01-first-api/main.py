"""Lostdesk, chapter 1: the lost-property office of a city metro, as a web API."""
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Things found on the trains today, by their id number.
FOUND = {
    1: {"id": 1, "title": "black umbrella", "station": "Riverside"},
    2: {"id": 2, "title": "blue school bag", "station": "Old Market"},
    3: {"id": 3, "title": "silver phone", "station": "Tech Park"},
    4: {"id": 4, "title": "bunch of keys", "station": "Riverside"},
}


@app.get("/")
def home():
    return {"message": "Lostdesk is open. Try /items"}


# TODO (task menu): GET /items gives back {"items": [...]}, every found item, in id order.


# TODO (task price): GET /items/{item_id} gives back that one item; an id that is not in FOUND gives 404.
