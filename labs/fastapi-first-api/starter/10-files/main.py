"""Lostdesk, chapter 10: headers, forms and files. Staff send a desk key; found items get a photo."""
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, Header, HTTPException, UploadFile, status

app = FastAPI()

DESK_KEY = "riverside-desk-7"  # chapter 16 replaces this with real sign-in
PHOTOS = Path("photos")
MAX_PHOTO_BYTES = 2 * 1024 * 1024
PHOTO_TYPES = {"image/jpeg": "jpg", "image/png": "png"}

FOUND: dict[int, dict] = {
    1: {"id": 1, "title": "black umbrella", "station": "Riverside", "photo": None},
    2: {"id": 2, "title": "blue school bag", "station": "Old Market", "photo": None},
}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    return FOUND[item_id]


@app.post("/items", status_code=status.HTTP_201_CREATED)
def log_found_item(
    title: Annotated[str, Form(min_length=3)],
    station: Annotated[str, Form()],
    # TODO (task desk_header): read the X-Desk-Key header; when it is missing or not DESK_KEY, answer 401.
):
    new_id = max(FOUND) + 1
    FOUND[new_id] = {"id": new_id, "title": title, "station": station, "photo": None}
    return FOUND[new_id]


# TODO (task upload_photo): POST /items/{item_id}/photo takes an uploaded file called photo. Refuse an unknown item
# (404), anything but JPEG or PNG (415) and files over 2 MB (413); save it as photos/<item_id>.jpg or .png and give
# back {"item_id": ..., "filename": <the uploaded name>, "saved_as": <the path>, "size": <bytes>}.
