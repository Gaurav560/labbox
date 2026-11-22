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
    profile = r.hgetall(f"customer:{cid}")
    if not profile:
        raise HTTPException(status_code=404, detail=f"No customer {cid}")
    return {"id": cid, "name": profile["name"], "orders": int(profile["orders"]), "tier": profile["tier"]}


@app.post("/import")
def import_sales():
    """Load data/sales.csv into the hash sales:import: field "<store>:<item>", value the units sold."""
    with open("data/sales.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    # One pipeline: every HSET is sent together, and Redis answers them all in one round trip.
    pipe = r.pipeline(transaction=False)
    for row in rows:
        pipe.hset("sales:import", f"{row['store']}:{row['item']}", row["units"])
    pipe.execute()
    return {"imported": len(rows)}
