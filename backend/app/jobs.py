"""Background jobs (Phase H3), run on a schedule by the worker (app/worker.py) or by hand
(`scripts/labbox jobs --run <name>`):

- images:   every image the labs need is on this machine (lab images are built here; public service
            images such as postgres:16 are pulled when missing), so no learner waits for a download.
- networks: lab networks that no machine uses any more are removed (Docker has a limited number).
- backup:   a copy of the database in BACKUP_DIR, the newest BACKUP_KEEP kept, each one checked.

Each run records its result (time, ok, summary) in shared state, so `scripts/labbox jobs` can show it.
"""
import json
import logging
import os
import re
import sqlite3
import subprocess
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from docker.errors import APIError, ImageNotFound, NotFound
from sqlalchemy.engine import make_url

from . import containers, services, shared
from .config import get_settings
from .labs import CHECKER_IMAGE, all_labs

log = logging.getLogger(__name__)

NETWORK_MIN_AGE_SECONDS = 3600  # never touch a network a machine may be about to join


@dataclass
class JobResult:
    job: str
    ok: bool
    summary: str
    at: str = ""
    seconds: float = 0


def _record(result: JobResult) -> JobResult:
    r = shared.redis_client()
    if r is not None:
        r.set(shared.PREFIX + "job:" + result.job, json.dumps(asdict(result)))
    (log.info if result.ok else log.error)("Job %s: %s", result.job, result.summary)
    return result


def last_runs() -> dict[str, dict]:
    r = shared.redis_client()
    if r is None:
        return {}
    out = {}
    for name in JOBS:
        raw = r.get(shared.PREFIX + "job:" + name)
        if raw:
            out[name] = json.loads(raw)
    return out


def run(name: str) -> JobResult:
    started = time.monotonic()
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        ok, summary = JOBS[name]()
    except Exception as e:  # a failed job is recorded, never raised into the worker
        log.exception("Job %s failed", name)
        ok, summary = False, f"{type(e).__name__}: {e}"
    return _record(JobResult(name, ok, summary, at, round(time.monotonic() - started, 1)))


# ---------- images ----------


def wanted_images() -> dict[str, bool]:
    """Every image the labs use, and whether it is built here (True) or pulled from a registry (False)."""
    out: dict[str, bool] = {CHECKER_IMAGE: True, services.RELAY_IMAGE: False}
    for lab in all_labs():
        out[lab.image] = True
        if lab.check.image:
            out.setdefault(lab.check.image, lab.check.image.startswith("labbox/"))
        for svc in lab.services:
            out.setdefault(svc.image, svc.image.startswith("labbox/"))
    return out


def images_job(pull: bool = True) -> tuple[bool, str]:
    client = containers.client()
    missing_built, pulled, failed = [], [], []
    for image, built_here in sorted(wanted_images().items()):
        try:
            client.images.get(image)
            continue
        except ImageNotFound:
            pass
        if built_here:
            missing_built.append(image)
        elif pull:
            try:
                client.images.pull(image)
                pulled.append(image)
            except APIError as e:
                failed.append(f"{image} ({e.explanation or e})")
        else:
            failed.append(image)
    parts = [f"{len(wanted_images())} images checked"]
    if pulled:
        parts.append("pulled " + ", ".join(pulled))
    if missing_built:
        parts.append("not built (run scripts/build_lab_images.sh): " + ", ".join(missing_built))
    if failed:
        parts.append("could not pull: " + ", ".join(failed))
    return not (missing_built or failed), "; ".join(parts)


# ---------- networks ----------


def _created(stamp: str) -> float:
    """Docker's '2026-11-20T00:45:01.817815011+05:30' (nanoseconds, any offset) as a Unix time; now if unreadable."""
    m = re.match(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d+))?(Z|[+-]\d\d:\d\d)?", stamp or "")
    if not m:
        return time.time()
    frac = (m.group(2) or "0")[:6].ljust(6, "0")
    zone = "+00:00" if m.group(3) in (None, "Z") else m.group(3)
    return datetime.fromisoformat(f"{m.group(1)}.{frac}{zone}").timestamp()


def networks_job(min_age: float = NETWORK_MIN_AGE_SECONDS) -> tuple[bool, str]:
    """Remove lab networks (labnet-u<id>-<lab>) that no container of that machine group uses, running or
    stopped. A stopped lab keeps its network, so it starts again exactly as it was."""
    client = containers.client()
    removed = []
    now = time.time()
    for net in containers.mine(client.networks.list(filters={"label": containers.label_filter("labbox.kind=network")})):
        labels = net.attrs.get("Labels") or {}
        user, lab = labels.get("labbox.user"), labels.get("labbox.lab")
        if not user or not lab:
            continue
        if now - _created(net.attrs.get("Created", "")) < min_age:
            continue
        machine = containers.container_name(int(user), lab)
        # The same lock as starting the machine, so a learner arriving right now is never cut off.
        with shared.lock(machine, wait=30):
            group = containers.mine(client.containers.list(all=True, filters={"label": [f"labbox.user={user}", f"labbox.lab={lab}"]}))
            if group:
                continue
            try:
                net.reload()
                net.remove()
                removed.append(net.name)
            except (NotFound, APIError) as e:
                log.warning("Could not remove network %s: %s", net.name, e)
    return True, f"removed {len(removed)} unused lab network(s)" + (f": {', '.join(removed)}" if removed else "")


# ---------- backup ----------


def backup_job() -> tuple[bool, str]:
    s = get_settings()
    folder = Path(s.BACKUP_DIR)
    folder.mkdir(parents=True, exist_ok=True)
    os.chmod(folder, 0o700)
    url = make_url(s.DATABASE_URL)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    if url.get_backend_name() == "postgresql":
        target = folder / f"labbox-{stamp}.dump"
        tables = _pg_dump(url, target)
    else:
        target = folder / f"labbox-{stamp}.sqlite"
        tables = _sqlite_copy(Path(url.database or ""), target)
    os.chmod(target, 0o600)
    kept = _rotate(folder, s.BACKUP_KEEP)
    return True, f"{target.name} ({target.stat().st_size // 1024} KB, {tables} tables checked); {kept} backups kept"


def _pg_image(url) -> str:
    from sqlalchemy import create_engine, text

    e = create_engine(url)
    try:
        with e.connect() as c:
            major = int(c.execute(text("SHOW server_version_num")).scalar()) // 10000
    finally:
        e.dispose()
    return f"postgres:{major}"  # pg_dump of the server's own version: its dumps restore anywhere with that version


def _pg_dump(url, target: Path) -> int:
    """pg_dump in a throwaway container of the server's version, written to a temporary name first.
    The password reaches the container through the environment, never the command line."""
    image = _pg_image(url)
    env = {**os.environ, "PGPASSWORD": url.password or ""}
    base = ["docker", "run", "--rm", "-i", "--network", "host", "-e", "PGPASSWORD", image]
    conn = ["-h", url.host or "127.0.0.1", "-p", str(url.port or 5432), "-U", url.username or "postgres"]
    part = target.with_suffix(".part")
    with open(part, "wb") as out:
        r = subprocess.run([*base, "pg_dump", "-Fc", *conn, url.database or "postgres"], stdout=out,
                           stderr=subprocess.PIPE, env=env, timeout=3600)
    if r.returncode != 0:
        part.unlink(missing_ok=True)
        raise RuntimeError(f"pg_dump failed: {r.stderr.decode(errors='replace')[-300:]}")
    # Check it: the archive's table of contents must list our tables' data.
    with open(part, "rb") as f:
        listing = subprocess.run([*base, "pg_restore", "--list"], stdin=f, capture_output=True, timeout=600)
    toc = listing.stdout.decode(errors="replace")
    tables = sum(1 for line in toc.splitlines() if " TABLE DATA " in line)
    if listing.returncode != 0 or not re.search(r' TABLE DATA public "?user"? ', toc):
        part.unlink(missing_ok=True)
        raise RuntimeError("the dump does not list the user table; not kept")
    part.rename(target)
    return tables


def _sqlite_copy(source: Path, target: Path) -> int:
    part = target.with_suffix(".part")
    src = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    dst = sqlite3.connect(part)
    try:
        src.backup(dst)  # a consistent copy even while the app writes
        tables = dst.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
        if dst.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("the copy failed its integrity check; not kept")
    finally:
        src.close()
        dst.close()
    part.rename(target)
    return tables


def _rotate(folder: Path, keep: int) -> int:
    backups = sorted(p for p in folder.glob("labbox-*") if p.suffix in (".dump", ".sqlite"))
    for old in backups[:-keep] if keep > 0 else []:
        old.unlink()
    return min(len(backups), keep)


JOBS: dict[str, Callable[[], tuple[bool, str]]] = {
    "images": images_job,
    "networks": networks_job,
    "backup": backup_job,
}
