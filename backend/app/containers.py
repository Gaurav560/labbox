"""ALL docker logic lives here. Every function is blocking: call it via asyncio.to_thread."""
import logging
import shutil
import shlex
import socket
import threading
import uuid
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Literal

import docker
from docker.errors import APIError, NotFound
from docker.models.containers import Container
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from . import workspace_files
from .config import get_settings
from .labs import LabConfig
from .models import User, Workspace, utcnow

log = logging.getLogger(__name__)

LEARNER_USER = f"{workspace_files.LEARNER_UID}:{workspace_files.LEARNER_GID}"
TOUCH_MIN_SECONDS = 30

Status = Literal["running", "stopped", "missing"]

# One lock per container name so a page load and a terminal connect cannot both create it.
_locks: defaultdict[str, threading.Lock] = defaultdict(threading.Lock)


@lru_cache
def client() -> docker.DockerClient:
    return docker.from_env()


def docker_ok() -> bool:
    try:
        return bool(client().ping())
    except Exception:
        return False


def container_name(user_id: int, lab_id: str) -> str:
    return f"lab-u{user_id}-{lab_id}"


def labels(kind: Literal["workspace", "check"], user_id: int, lab_id: str) -> dict[str, str]:
    return {"labbox": "true", "labbox.kind": kind, "labbox.user": str(user_id), "labbox.lab": lab_id}


def security_options(lab: LabConfig) -> dict:
    """Limits shared by workspace and check containers."""
    return dict(
        user=LEARNER_USER,
        nano_cpus=int(lab.resources.cpus * 1e9),
        mem_limit=lab.resources.memory,
        memswap_limit=lab.resources.memory,  # no swap
        cap_drop=["ALL"],
        security_opt=["no-new-privileges:true"],
        runtime=get_settings().CONTAINER_RUNTIME or None,
    )


# ---------- workspace rows and host folders ----------


def get_workspace(session: Session, user: User, lab: LabConfig) -> Workspace:
    """Get or create the Workspace row, its host folder, and seed starter files once."""
    assert user.id is not None
    ws = session.exec(select(Workspace).where(Workspace.user_id == user.id, Workspace.lab_id == lab.id)).first()
    if ws is None:
        folder = get_settings().VOLUMES_DIR / f"u{user.id}" / lab.id
        ws = Workspace(
            user_id=user.id, lab_id=lab.id, container_name=container_name(user.id, lab.id), volume_path=str(folder)
        )
        session.add(ws)
        try:
            session.commit()
        except IntegrityError:
            # Another request created it at the same moment.
            session.rollback()
            return get_workspace(session, user, lab)
        session.refresh(ws)
    folder = Path(ws.volume_path)
    if not folder.is_dir():
        folder.mkdir(parents=True, exist_ok=True)
        workspace_files.chown(folder.parent)
        workspace_files.chown(folder)
    if not ws.seeded:
        seed(lab, folder)
        ws.seeded = True
        session.add(ws)
        session.commit()
    return ws


def seed(lab: LabConfig, folder: Path) -> None:
    """Copy starter/ (never tests/) into the workspace folder."""
    if lab.starter_dir.is_dir():
        shutil.copytree(lab.starter_dir, folder, dirs_exist_ok=True, symlinks=True)
    workspace_files.chown_tree(folder)
    log.info("Seeded %s with starter files of %s", folder, lab.id)


def touch(session: Session, ws: Workspace, force: bool = True) -> None:
    now = utcnow()
    if not force and (now - ws.last_active_at).total_seconds() < TOUCH_MIN_SECONDS:
        return
    ws.last_active_at = now
    session.add(ws)
    session.commit()


# ---------- containers ----------


def _get(name: str) -> Container | None:
    try:
        return client().containers.get(name)
    except NotFound:
        return None


def container_status(name: str) -> Status:
    c = _get(name)
    if c is None:
        return "missing"
    return "running" if c.status == "running" else "stopped"


def _create(lab: LabConfig, ws: Workspace) -> Container:
    mount = lab.workspace.mount_path
    c = client().containers.run(
        image=lab.image,
        name=ws.container_name,
        detach=True,
        labels=labels("workspace", ws.user_id, lab.id),
        hostname=lab.id,
        working_dir=mount,
        volumes={ws.volume_path: {"bind": mount, "mode": "rw"}},
        pids_limit=lab.resources.pids_limit,  # stops fork bombs
        network_mode=lab.workspace.network,
        tty=True,
        stdin_open=True,
        command=["sleep", "infinity"],
        init=True,  # tini as PID 1: stops in milliseconds (sleep ignores SIGTERM as PID 1) and reaps zombies
        environment={"HOME": "/home/learner", "TERM": "xterm-256color"},
        **security_options(lab),
    )
    log.info("Created container %s from %s", ws.container_name, lab.image)
    return c


def ensure_workspace(session: Session, user: User, lab: LabConfig) -> Workspace:
    """Make sure the user's container for this lab exists and is running."""
    ws = get_workspace(session, user, lab)
    with _locks[ws.container_name]:
        # Touch under the lock so the reaper's re-check sees this visit and does not stop us.
        touch(session, ws)
        c = _get(ws.container_name)
        try:
            if c is None:
                _create(lab, ws)
            elif c.status != "running":
                c.start()
                log.info("Started container %s", ws.container_name)
        except docker.errors.ImageNotFound:
            raise HTTPException(500, f"Lab image {lab.image} is not built. Run scripts/build_lab_images.sh")
        except APIError as e:
            log.exception("Could not start %s", ws.container_name)
            raise HTTPException(500, f"Could not start your machine: {e.explanation or e}")
    return ws


def stop_workspace(name: str) -> None:
    c = _get(name)
    if c is not None and c.status == "running":
        c.stop(timeout=5)
        log.info("Stopped container %s", name)


def reset_workspace(session: Session, user: User, lab: LabConfig) -> Workspace:
    """Delete the container and all files, re-seed starter files, start a new container."""
    ws = get_workspace(session, user, lab)
    with _locks[ws.container_name]:
        c = _get(ws.container_name)
        if c is not None:
            c.remove(force=True)
            log.info("Removed container %s for reset", ws.container_name)
        workspace_files.clear_dir(Path(ws.volume_path))
        ws.seeded = False
        session.add(ws)
        session.commit()
    return ensure_workspace(session, user, lab)


def running_workspace_containers() -> dict[str, Container]:
    found = client().containers.list(filters={"label": ["labbox=true", "labbox.kind=workspace"]})
    return {c.name: c for c in found}


def stop_idle(session: Session, older_than: datetime) -> list[str]:
    """Stop running workspace containers whose last activity is before older_than."""
    running = running_workspace_containers()
    if not running:
        return []
    idle = session.exec(
        select(Workspace).where(Workspace.last_active_at < older_than, Workspace.container_name.in_(list(running)))  # type: ignore[attr-defined]
    ).all()
    stopped = []
    for ws in idle:
        with _locks[ws.container_name]:
            # Re-check under the lock in case the user came back meanwhile.
            session.refresh(ws)
            if ws.last_active_at >= older_than:
                continue
            try:
                running[ws.container_name].stop(timeout=5)
                stopped.append(ws.container_name)
            except NotFound:
                pass
    return stopped


def remove_old_check_containers(max_age_seconds: float) -> list[str]:
    removed = []
    for c in client().containers.list(all=True, filters={"label": ["labbox=true", "labbox.kind=check"]}):
        created = datetime.fromisoformat(c.attrs["Created"].split(".")[0].rstrip("Z"))
        if (utcnow() - created).total_seconds() > max_age_seconds:
            c.remove(force=True)
            removed.append(c.name)
    return removed


# ---------- interactive shell (used by terminal.py) ----------


def open_shell(lab: LabConfig, ws: Workspace) -> tuple[str, socket.socket, str]:
    """Start a login shell with a TTY in the workspace container.

    Returns (exec_id, raw socket, session_file). The shell is a session leader (docker
    exec with a TTY calls setsid), and the wrapper writes its pid to session_file so
    close_shell() can kill the whole session when the browser goes away.
    """
    api = client().api
    session_file = f"/tmp/.labbox-term-{uuid.uuid4().hex}"
    exec_id = api.exec_create(
        ws.container_name,
        cmd=["/bin/sh", "-c", f"echo $$ > {session_file}; exec {shlex.quote(lab.workspace.shell)} -l"],
        stdin=True,
        stdout=True,
        stderr=True,
        tty=True,
        user=LEARNER_USER,
        workdir=lab.workspace.mount_path,
        environment={"TERM": "xterm-256color", "HOME": "/home/learner"},
    )["Id"]
    sock = api.exec_start(exec_id, tty=True, socket=True)
    raw: socket.socket = sock._sock  # docker-py wraps the real socket
    raw.setblocking(True)
    return exec_id, raw, session_file


def resize_shell(exec_id: str, cols: int, rows: int) -> None:
    client().api.exec_resize(exec_id, height=rows, width=cols)


def close_shell(container: str, raw: socket.socket, session_file: str) -> None:
    """Close the socket (wakes any blocked recv) and end every process in the shell's session.

    Docker does not kill an exec when its client disconnects, so without this every closed
    tab would leave a bash (and whatever it was running) behind.
    """
    try:
        raw.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    raw.close()
    script = (
        f'sid=$(cat {session_file} 2>/dev/null) && rm -f {session_file} && [ -n "$sid" ] '
        '&& pkill -HUP -s "$sid"; sleep 1; [ -n "$sid" ] && pkill -KILL -s "$sid"; true'
    )
    try:
        client().api.exec_start(client().api.exec_create(container, ["/bin/sh", "-c", script], user=LEARNER_USER)["Id"], detach=True)
    except (APIError, NotFound):
        pass  # container already stopped or removed: nothing left to kill
