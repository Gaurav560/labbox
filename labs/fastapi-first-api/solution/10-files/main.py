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
    x_desk_key: Annotated[str | None, Header()] = None,
):
    if x_desk_key != DESK_KEY:
        raise HTTPException(status_code=401, detail="Only staff at a desk can log items")
    new_id = max(FOUND) + 1
    FOUND[new_id] = {"id": new_id, "title": title, "station": station, "photo": None}
    return FOUND[new_id]


@app.post("/items/{item_id}/photo")
async def upload_photo(item_id: int, photo: UploadFile):
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    if photo.content_type not in PHOTO_TYPES:
        raise HTTPException(status_code=415, detail="Send a JPEG or PNG photo")
    data = await photo.read()
    if len(data) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=413, detail="The photo is larger than 2 MB")
    PHOTOS.mkdir(exist_ok=True)
    path = PHOTOS / f"{item_id}.{PHOTO_TYPES[photo.content_type]}"
    path.write_bytes(data)
    FOUND[item_id]["photo"] = str(path)
    return {"item_id": item_id, "filename": photo.filename, "saved_as": str(path), "size": len(data)}
