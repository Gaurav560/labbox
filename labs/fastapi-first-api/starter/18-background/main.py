"""Lostdesk, chapter 18: async and background tasks. Answer at once; send the slow message afterwards."""
import asyncio
import time
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException

app = FastAPI()

OUTBOX = Path("outbox.log")

FOUND = {1: {"id": 1, "title": "grey laptop bag", "station": "Tech Park"}}
REPORTS = {1: {"id": 1, "title": "grey laptop bag", "contact": "98200 11111"}}


def send_text_message(contact: str, message: str) -> None:
    """Pretends to send an SMS. A real gateway often takes a second or more to answer."""
    time.sleep(1.5)
    with OUTBOX.open("a") as outbox:
        outbox.write(f"to {contact}: {message}\n")


async def search_reports(q: str) -> list[str]:
    """Pretends to ask the reports service: about 0.4 seconds."""
    await asyncio.sleep(0.4)
    return [r["title"] for r in REPORTS.values() if q in r["title"]]


async def search_station_logs(q: str) -> list[str]:
    """Pretends to ask the stations' handwritten logs, scanned: about 0.4 seconds."""
    await asyncio.sleep(0.4)
    return [f"{i['title']} seen at {i['station']}" for i in FOUND.values() if q in i["title"]]


# TODO (task notify_background): the passenger waits 1.5 seconds for this answer because the text message is sent first.
# Take background_tasks: BackgroundTasks and add send_text_message to it, so it runs after the answer has gone.
@app.post("/items/{item_id}/match/{report_id}")
def match(item_id: int, report_id: int):
    if item_id not in FOUND or report_id not in REPORTS:
        raise HTTPException(status_code=404, detail="No such item or report")
    report = REPORTS[report_id]
    message = f"Lostdesk: a {report['title']} has been found. Bring ID to the {FOUND[item_id]['station']} desk."
    send_text_message(report["contact"], message)
    return {"item_id": item_id, "report_id": report_id, "notice": "queued"}


@app.get("/search")
async def search(q: str):
    # TODO (task parallel_search): these two searches run one after the other (about 0.8 s). Run them at the same
    # time with asyncio.gather, so the answer takes about as long as the slower one.
    reports = await search_reports(q)
    logs = await search_station_logs(q)
    return {"reports": reports, "logs": logs}
