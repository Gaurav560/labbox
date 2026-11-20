"""The background worker (Phase H3): runs app/jobs.py on a schedule, next to the backend.

    cd backend && .venv/bin/arq app.worker.WorkerSettings

It needs REDIS_URL (arq keeps its schedule there). Several workers, or several servers, can run it:
arq runs each scheduled job once. Schedule (UTC):
- images:   at start and every day at 03:00
- networks: at start and every hour at :15
- backup:   every day at BACKUP_HOUR_UTC (21:00, which is 02:30 in India)
"""
import asyncio
import logging
from datetime import timezone

from arq import cron
from arq.connections import RedisSettings

from . import jobs
from .config import get_settings
from .labs import init_labs

log = logging.getLogger(__name__)


async def startup(ctx: dict) -> None:
    # arq logs its own lines; LabBox's jobs log through "app" (not the root logger: no double lines).
    app_log = logging.getLogger("app")
    if not app_log.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        app_log.addHandler(h)
        app_log.setLevel(logging.INFO)
        app_log.propagate = False
    init_labs(get_settings().LABS_DIR)  # the images job needs the labs
    log.info("LabBox worker started")


def _job(name: str):
    async def run(ctx: dict) -> dict:
        result = await asyncio.to_thread(jobs.run, name)
        return {"ok": result.ok, "summary": result.summary}

    run.__qualname__ = run.__name__ = f"job_{name}"
    return run


job_images, job_networks, job_backup = _job("images"), _job("networks"), _job("backup")


def _redis() -> RedisSettings:
    url = get_settings().REDIS_URL
    if not url:
        raise SystemExit("The worker needs REDIS_URL in backend/.env (scripts/devdb.sh url).")
    return RedisSettings.from_dsn(url)


class WorkerSettings:
    redis_settings = _redis()
    on_startup = startup
    functions: list = []
    cron_jobs = [
        cron(job_images, hour={3}, minute={0}, run_at_startup=True, timeout=3600),
        cron(job_networks, minute={15}, run_at_startup=True, timeout=600),
        cron(job_backup, hour={get_settings().BACKUP_HOUR_UTC}, minute={0}, timeout=3600),
    ]
    # The schedule above is in UTC (arq would otherwise use the machine's own zone: on this laptop India
    # time, which put the "02:30" backup at 21:00 local).
    timezone = timezone.utc
    job_timeout = 3600
    keep_result = 7 * 24 * 3600
    queue_name = "labbox:arq"
