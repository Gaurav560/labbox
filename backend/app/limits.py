"""Safety limits (Phase H5): one learner, or one runaway program, can never take the server down for
everyone. Every limit is a setting (app/config.py); 0 turns it off.

- Disk: a learner's own files (all labs together) and each lab's databases have a ceiling. Measured
  here (this laptop's ext4 has no quotas switched on); a server can add hard filesystem quotas later.
- Running labs: at most MAX_RUNNING_LABS per learner; starting another stops the least recently used.
- Session: a machine running SESSION_HOURS is stopped.
- CPU: a machine using all of its CPU for CPU_STUCK_MINUTES (an endless loop) is stopped.
- Rate limits per IP address on sign up, failed logins and checks.

A machine stopped by a limit keeps its files, and the lab page says why it stopped (stop_reason).
"""
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, Request
from docker.errors import NotFound
from sqlmodel import Session, select

from . import containers, services, shared
from .config import get_settings
from .labs import LabConfig, get_lab
from .models import Workspace

log = logging.getLogger(__name__)

REASON_SECONDS = 7 * 24 * 3600
DISK_CACHE_SECONDS = 30  # autosave writes every half second; the size is measured at most this often
CPU_BUSY_SHARE = 0.9  # "all its CPU": at least this share of its limit, round after round
CGROUP = Path("/sys/fs/cgroup/system.slice")


# ---------- why a machine stopped ----------


def set_reason(container: str, reason: str) -> None:
    shared.put(f"stopped:{container}", reason, REASON_SECONDS)


def stop_reason(container: str) -> str | None:
    return shared.get(f"stopped:{container}")


def clear_reason(container: str) -> None:
    shared.delete(f"stopped:{container}")


def stop_machine(ws: Workspace, reason: str) -> None:
    """Stop a machine and its services because of a limit; its files stay."""
    with shared.lock(ws.container_name, wait=60):
        containers.stop_workspace(ws.container_name)
        try:
            services.stop_services(get_lab(ws.lab_id), ws)
        except HTTPException:
            pass  # the lab no longer exists
    set_reason(ws.container_name, reason)
    log.info("Limit stopped %s: %s", ws.container_name, reason)


# ---------- disk ----------


def folder_mb(path: Path) -> float:
    """Size of everything under path in MB, never following links."""
    total = 0
    stack = [path]
    while stack:
        try:
            with os.scandir(stack.pop()) as it:
                for e in it:
                    try:
                        if e.is_dir(follow_symlinks=False):
                            stack.append(Path(e.path))
                        else:
                            total += e.stat(follow_symlinks=False).st_size
                    except OSError:
                        pass
        except OSError:
            pass
    return total / (1024 * 1024)


def learner_files_mb(user_id: int, fresh: bool = False) -> float:
    """The learner's own files in all their labs (not the labs' databases, which the lab seeds)."""
    key = f"disk:{user_id}"
    if not fresh and (cached := shared.get(key)) is not None:
        return float(cached)
    home = get_settings().VOLUMES_DIR / f"u{user_id}"
    mb = sum(folder_mb(p) for p in home.iterdir() if p.is_dir() and not p.name.endswith(".services")) if home.is_dir() else 0.0
    shared.put(key, f"{mb:.1f}", DISK_CACHE_SECONDS)
    return mb


def service_data_mb(ws: Workspace) -> float:
    return folder_mb(Path(f"{ws.volume_path}.services"))


def disk_message(used: float, quota: int, stopped: bool = False) -> str:
    start = "Stopped because your files use" if stopped else "Your files use"
    return (f"{start} {used:.0f} MB of your {quota} MB. Delete files you do not need, or reset a lab, "
            "then start your machine again.")


def check_disk(user_id: int, fresh: bool = False) -> None:
    """507 when the learner's files are over the quota (saving and starting a machine are refused;
    deleting files and resetting a lab still work)."""
    quota = get_settings().DISK_QUOTA_MB
    if quota and (used := learner_files_mb(user_id, fresh)) > quota:
        raise HTTPException(507, disk_message(used, quota))


def check_service_data(lab: LabConfig, ws: Workspace) -> None:
    cap = get_settings().SERVICE_DATA_MAX_MB
    if cap and lab.services and (used := service_data_mb(ws)) > cap:
        raise HTTPException(507, f"This lab's database grew to {used:.0f} MB (the limit is {cap} MB). Reset the lab to start fresh.")


# ---------- running labs per learner ----------


def _running_for(user_id: int) -> list:
    return containers.client().containers.list(
        filters={"label": ["labbox=true", "labbox.kind=workspace", f"labbox.user={user_id}"], "status": "running"}
    )


def make_room(session: Session, user_id: int, lab: LabConfig) -> list[str]:
    """Before a learner's machine starts: if they already run MAX_RUNNING_LABS others, stop the least
    recently used ones. Returns the stopped machines' names."""
    limit = get_settings().MAX_RUNNING_LABS
    if not limit:
        return []
    me = containers.container_name(user_id, lab.id)
    stopped = []
    with shared.lock(f"user:{user_id}:machines", wait=30):
        others = [c.name for c in _running_for(user_id) if c.name != me]
        if len(others) < limit:
            return []
        rows = session.exec(select(Workspace).where(Workspace.container_name.in_(others))).all()  # type: ignore[attr-defined]
        rows = sorted(rows, key=lambda w: w.last_active_at)  # least recently used first
        for ws in rows[: len(others) - limit + 1]:
            stop_machine(ws, f"Stopped to make room for {lab.title}: you can run {limit} labs at once. Your files are kept.")
            stopped.append(ws.container_name)
    return stopped


# ---------- the reaper's round: session, CPU, disk ----------


def _started(c) -> float:
    raw = c.attrs.get("State", {}).get("StartedAt", "")
    try:
        return datetime.fromisoformat(raw[:26].rstrip("Z") + "+00:00").timestamp()
    except ValueError:
        return time.time()


def cpu_usage_usec(container_id: str) -> int | None:
    try:
        for line in (CGROUP / f"docker-{container_id}.scope" / "cpu.stat").read_text().splitlines():
            if line.startswith("usage_usec "):
                return int(line.split()[1])
    except OSError:
        return None
    return None


def cpu_stuck(c, now: float) -> bool:
    """True once the machine has used at least CPU_BUSY_SHARE of its CPU limit for CPU_STUCK_MINUTES.
    Each round compares the counter with the last round's (kept in shared state)."""
    minutes = get_settings().CPU_STUCK_MINUTES
    usage = cpu_usage_usec(c.id)
    if not minutes or usage is None:
        return False
    cpus = (c.attrs.get("HostConfig", {}).get("NanoCpus") or 0) / 1e9 or (os.cpu_count() or 1)
    key = f"cpu:{c.name}"
    prev = json.loads(shared.get(key) or "null")
    busy_since = None
    if prev and now > prev["t"]:
        share = (usage - prev["u"]) / ((now - prev["t"]) * 1e6 * cpus)
        if share >= CPU_BUSY_SHARE:
            busy_since = prev.get("since") or prev["t"]
    shared.put(key, json.dumps({"u": usage, "t": now, "since": busy_since}), 3600)
    return busy_since is not None and now - busy_since >= minutes * 60


def enforce(session: Session) -> list[tuple[str, str]]:
    """One pass over running machines (the reaper's leader runs it every round)."""
    s = get_settings()
    now = time.time()
    stopped: list[tuple[str, str]] = []
    disk: dict[int, float] = {}
    for c in containers.running_workspace_containers().values():
        ws = session.exec(select(Workspace).where(Workspace.container_name == c.name)).first()
        if ws is None:
            continue  # not a learner's machine in this database
        reason = None
        if s.SESSION_HOURS and now - _started(c) > s.SESSION_HOURS * 3600:
            reason = (f"Stopped after {s.SESSION_HOURS:g} hours of running, so machines stay free for everyone. "
                      "Your files are kept: start it again to continue.")
        elif cpu_stuck(c, now):
            reason = (f"Stopped because it used all its CPU for {s.CPU_STUCK_MINUTES:g} minutes (often an endless loop). "
                      "Your files are kept: fix the loop, then start it again.")
        else:
            if ws.user_id not in disk:
                disk[ws.user_id] = learner_files_mb(ws.user_id, fresh=True)
            if s.DISK_QUOTA_MB and disk[ws.user_id] > s.DISK_QUOTA_MB:
                reason = disk_message(disk[ws.user_id], s.DISK_QUOTA_MB, stopped=True)
            else:
                try:
                    check_service_data(get_lab(ws.lab_id), ws)
                except HTTPException as e:
                    reason = "Stopped: " + str(e.detail)
        if reason:
            try:
                stop_machine(ws, reason)
                stopped.append((c.name, reason))
            except (NotFound, shared.Busy):
                pass
    return stopped


# ---------- rate limits per IP address ----------


def client_ip(request: Request) -> str:
    # Behind nginx, uvicorn --proxy-headers puts the real address here (deploy/labbox.service).
    return request.client.host if request.client else "unknown"


def too_many(key: str, limit: int, window: float, message: str) -> None:
    if limit and shared.recent(key, window) >= limit:
        raise HTTPException(429, message, headers={"Retry-After": str(int(window))})
