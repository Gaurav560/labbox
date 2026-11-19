"""Background task: stop idle workspace containers and clean up check leftovers."""
import asyncio
import logging
import os
import shutil
import socket
import time
from datetime import timedelta

from sqlmodel import Session

from . import containers, limits, shared
from .config import get_settings
from .db import engine
from .models import utcnow

log = logging.getLogger(__name__)

CHECK_LEFTOVER_SECONDS = 5 * 60


def reap_once() -> None:
    settings = get_settings()
    cutoff = utcnow() - timedelta(minutes=settings.IDLE_STOP_MINUTES)
    with Session(engine) as session:
        for name in containers.stop_idle(session, cutoff):
            log.info("Reaper stopped idle container %s", name)
        limits.enforce(session)  # session length, stuck CPU, disk (Phase H5)
    for name in containers.remove_old_check_containers(CHECK_LEFTOVER_SECONDS):
        log.info("Reaper removed leftover check container %s", name)
    for d in settings.CHECKS_DIR.iterdir():
        if d.is_dir() and time.time() - d.stat().st_mtime > CHECK_LEFTOVER_SECONDS:
            shutil.rmtree(d, ignore_errors=True)
            log.info("Reaper removed leftover check folder %s", d)


async def reaper_loop() -> None:
    """Every worker runs this loop, but only the one holding the "reaper" lease reaps. The lease lasts three
    rounds and its holder renews it each round, so if that worker dies another one takes over."""
    interval = get_settings().REAPER_INTERVAL_SECONDS
    me = f"{socket.gethostname()}:{os.getpid()}"
    log.info("Reaper started: every %ss, idle limit %s min", interval, get_settings().IDLE_STOP_MINUTES)
    leading = False
    while True:
        try:
            now_leading = await asyncio.to_thread(shared.keep, "reaper", me, interval * 3)
            if now_leading != leading:
                log.info("Reaper: %s", "this worker reaps" if now_leading else "another worker reaps")
                leading = now_leading
            if leading:
                await asyncio.to_thread(reap_once)
        except Exception:
            log.exception("Reaper pass failed")
        await asyncio.sleep(interval)
