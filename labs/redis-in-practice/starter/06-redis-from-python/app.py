"""Basket's customer service (chapter 6). Run it from this folder:

    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Try it from a second terminal:  curl localhost:8000/customers/42
"""
import csv
import os

import redis
from fastapi import FastAPI, HTTPException

app = FastAPI()
# decode_responses=True: Redis answers with str instead of bytes.
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)


@app.get("/customers/{cid}")
def customer(cid: int):
    # TODO (task profile_api): read the hash customer:<cid>. Answer 404 when there is no such customer,
    # otherwise {"id": cid, "name": ..., "orders": <a number, not text>, "tier": ...}.
    raise HTTPException(status_code=501, detail="Not written yet")


@app.post("/import")
def import_sales():
    """Load data/sales.csv into the hash sales:import: field "<store>:<item>", value the units sold."""
    with open("data/sales.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    # TODO (task bulk_import): this works, but it makes one round trip to Redis per row. Make it fast.
    for row in rows:
        r.hset("sales:import", f"{row['store']}:{row['item']}", row["units"])
    return {"imported": len(rows)}
