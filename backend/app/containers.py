"""ALL docker logic lives here. Every function is blocking: call it via asyncio.to_thread."""
import json
import logging
import shutil
import shlex
import socket
import uuid
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

from . import ide, services, shared, workspace_files
from .config import get_settings
from .labs import LabConfig, get_lab
from .models import ChapterProgress, User, Workspace, utcnow

log = logging.getLogger(__name__)

LEARNER_USER = f"{workspace_files.LEARNER_UID}:{workspace_files.LEARNER_GID}"
TOUCH_MIN_SECONDS = 30

Status = Literal["running", "stopped", "missing"]

# One lock per container name so a page load and a terminal connect cannot both create it, even when
# they reach different workers (shared.lock lives in Redis when REDIS_URL is set).


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


def labels(kind: Literal["workspace", "check", "service", "network"], user_id: int, lab_id: str) -> dict[str, str]:
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
        # Two first requests (often on different workers) both see "not seeded": one copies, the other
        # waits and then finds it done.
        with shared.lock(f"{ws.container_name}:seed"):
            session.refresh(ws)
            if not ws.seeded:
                seed(lab, folder)
                ws.seeded = True
                session.add(ws)
                session.commit()
    else:
        top_up(lab, ws)
    return ws


def seed(lab: LabConfig, folder: Path) -> None:
    """Copy starter/ (never tests/) into the workspace folder."""
    if lab.starter_dir.is_dir():
        shutil.copytree(lab.starter_dir, folder, dirs_exist_ok=True, symlinks=True)
    workspace_files.chown_tree(folder)
    _write_record(folder, starter_files(lab))
    log.info("Seeded %s with starter files of %s", folder, lab.id)


# ---------- new starter files for labs that grow ----------
# A lab that gains chapters gains starter files (chapter 2's numbers_text.py...). Learners who opened the
# lab before only got the old ones. top_up copies the starter files they never received: never over
# their own files, and never again once received (a file they deleted stays deleted). The record of
# what each learner received lives next to their folder, outside /workspace.


@lru_cache(maxsize=256)
def _starter_files_cached(starter_dir: str) -> tuple[str, ...]:
    root = Path(starter_dir)
    if not root.is_dir():
        return ()
    return tuple(sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() or p.is_symlink()))


def starter_files(lab: LabConfig) -> tuple[str, ...]:
    """The lab's starter files, as paths relative to starter/ (labs load at startup, so this is cached)."""
    return _starter_files_cached(str(lab.starter_dir))


def _record_path(folder: Path) -> Path:
    return Path(f"{folder}.starter.json")


def _write_record(folder: Path, files) -> None:
    _record_path(folder).write_text(json.dumps(sorted(files)), encoding="utf-8")


def _read_record(folder: Path) -> set[str] | None:
    try:
        return set(json.loads(_record_path(folder).read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return None  # a workspace from before the record existed


def top_up(lab: LabConfig, ws: Workspace) -> list[str]:
    """Copy starter files this learner never received. Returns the files copied."""
    folder = Path(ws.volume_path)
    files = starter_files(lab)
    known = _read_record(folder)
    if known is not None and known.issuperset(files):
        return []  # the usual case: one small file read
    added: list[str] = []
    with shared.lock(f"{ws.container_name}:seed"):
        known = _read_record(folder) or set()
        root = folder.resolve()
        for rel in files:
            if rel in known:
                continue
            dst = folder / rel
            if dst.exists() or dst.is_symlink():
                continue  # the learner's own file with that name wins
            parent = dst.parent
            # Never follow a link the learner made out of their folder.
            if parent.exists() and not parent.resolve().is_relative_to(root):
                log.warning("Not topping up %s in %s: its folder leads outside the workspace", rel, folder)
                continue
            parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(lab.starter_dir / rel, dst, follow_symlinks=False)
            workspace_files.chown(dst)
            for d in dst.relative_to(folder).parents:
                if str(d) != ".":
                    workspace_files.chown(folder / d)
            added.append(rel)
        _write_record(folder, known | set(files))
    if added:
        log.info("Topped up %s with new starter files of %s: %s", folder, lab.id, ", ".join(added))
    return added


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


def _network_args(lab: LabConfig, ws: Workspace) -> dict:
    """network: lab (or none with services) joins only the private lab network; bridge keeps the
    normal Docker network and gets the lab network added after start (see _create)."""
    if lab.uses_lab_network and lab.workspace.network in ("lab", "none"):
        return dict(network=services.network_name(ws), networking_config=services.networking_config(ws, services.WORKSPACE_ALIAS))
    return dict(network_mode=lab.workspace.network)


def _ide_memory(lab: LabConfig) -> dict:
    """VS Code runs inside the machine, so the machine gets room for it on top of the lab's own limit."""
    if not ide.available():
        return {}
    m = lab.resources.memory.lower()
    mb = int(m[:-1]) * (1024 if m.endswith("g") else 1) + get_settings().IDE_EXTRA_MEMORY_MB
    return {"mem_limit": f"{mb}m", "memswap_limit": f"{mb}m"}


def llm_env(lab: LabConfig, ws: Workspace) -> dict[str, str]:
    """What an llm.enabled lab gets: the gateway's address and a key that only works there, for this
    user and lab. The real provider keys never enter a container."""
    if not lab.llm.enabled:
        return {}
    from .llm_gateway import create_lab_token

    base = f"http://{services.GATEWAY_ALIAS}:{get_settings().LLM_GATEWAY_PORT}"
    token = create_lab_token(ws.user_id, lab.id)
    return {
        "LABBOX_GATEWAY": base,
        "OPENAI_BASE_URL": f"{base}/llm/v1",
        "OPENAI_API_KEY": token,
        "ANTHROPIC_BASE_URL": f"{base}/llm/anthropic",
        "ANTHROPIC_API_KEY": token,
    }


def _create(lab: LabConfig, ws: Workspace) -> Container:
    mount = lab.workspace.mount_path
    c = client().containers.run(
        image=lab.image,
        name=ws.container_name,
        detach=True,
        labels=labels("workspace", ws.user_id, lab.id),
        hostname=lab.id,
        working_dir=mount,
        volumes={ws.volume_path: {"bind": mount, "mode": "rw"}, **ide.mounts()},
        pids_limit=lab.resources.pids_limit,  # stops fork bombs
        **_network_args(lab, ws),
        tty=True,
        stdin_open=True,
        command=["sleep", "infinity"],
        init=True,  # tini as PID 1: stops in milliseconds (sleep ignores SIGTERM as PID 1) and reaps zombies
        environment={**lab.workspace.env, **llm_env(lab, ws), "HOME": "/home/learner", "TERM": "xterm-256color"},
        **{**security_options(lab), **_ide_memory(lab)},
    )
    if lab.uses_lab_network and lab.workspace.network == "bridge":
        services.attach(c, ws, services.WORKSPACE_ALIAS)
    log.info("Created container %s from %s", ws.container_name, lab.image)
    return c


def ensure_workspace(session: Session, user: User, lab: LabConfig) -> Workspace:
    """Make sure the user's container for this lab exists and is running."""
    ws = get_workspace(session, user, lab)
    if container_status(ws.container_name) != "running":
        # Safety limits (Phase H5) before anything starts: disk, the lab's databases, running labs.
        from . import limits

        assert user.id is not None
        limits.check_disk(user.id, fresh=True)
        limits.check_service_data(lab, ws)
        limits.make_room(session, user.id, lab)
    with shared.lock(ws.container_name):
        # Touch under the lock so the reaper's re-check sees this visit and does not stop us.
        touch(session, ws)
        c = _get(ws.container_name)
        try:
            # Services first, so the database already answers when the learner's code starts.
            if lab.uses_lab_network:
                services.ensure_services(lab, ws)
            if c is None:
                _create(lab, ws)
            elif c.status != "running":
                c.start()
                log.info("Started container %s", ws.container_name)
                from . import limits

                limits.clear_reason(ws.container_name)  # running again: the old "why it stopped" is history
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


def stop_group(session: Session, user: User, lab: LabConfig) -> str:
    """Stop the workspace and its services together. Returns the workspace container name."""
    from . import limits

    ws = get_workspace(session, user, lab)
    with shared.lock(ws.container_name):
        stop_workspace(ws.container_name)
        services.stop_services(lab, ws)
    limits.clear_reason(ws.container_name)  # the learner stopped it: no limit to explain
    return ws.container_name


def upgrade_for_ide(session: Session, user: User, lab: LabConfig) -> None:
    """Machines created before VS Code was set up lack its mount (and, for labs without a network, the
    private network VS Code is reached through). Recreate such a machine: /workspace lives on the host
    and the learner's home folder is copied across, so nothing of theirs is lost."""
    if not ide.available():
        return
    ws = get_workspace(session, user, lab)
    with shared.lock(ws.container_name):
        c = _get(ws.container_name)
        if c is None:
            return
        has_mount = any(m.get("Destination") == ide.MOUNT for m in c.attrs.get("Mounts", []))
        nets = c.attrs.get("NetworkSettings", {}).get("Networks", {})
        has_net = not lab.uses_lab_network or services.network_name(ws) in nets
        if has_mount and has_net:
            return
        home = None
        try:
            if c.status != "running":
                c.start()
            home, _ = c.get_archive("/home/learner")
            home = b"".join(home)
        except (APIError, docker.errors.NotFound):
            log.warning("Could not copy the home folder of %s; it starts fresh", ws.container_name)
        c.remove(force=True)
        log.info("Recreating %s for VS Code", ws.container_name)
        if lab.uses_lab_network:
            services.ensure_services(lab, ws)
        new = _create(lab, ws)
        if home:
            new.put_archive("/home", home)


def reset_workspace(session: Session, user: User, lab: LabConfig) -> Workspace:
    """Delete the container and all files, re-seed starter files, start a new container."""
    ws = get_workspace(session, user, lab)
    with shared.lock(ws.container_name):
        c = _get(ws.container_name)
        if c is not None:
            c.remove(force=True)
            log.info("Removed container %s for reset", ws.container_name)
        services.remove_services(lab, ws, wipe_data=True)
        workspace_files.clear_dir(Path(ws.volume_path))
        ws.seeded = False
        session.add(ws)
        # Chapter setup (seed data, injected failures) runs again on the fresh machine.
        for cp in session.exec(select(ChapterProgress).where(ChapterProgress.user_id == ws.user_id, ChapterProgress.lab_id == lab.id)).all():
            cp.setup_done, cp.started_at = False, None
            session.add(cp)
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
        with shared.lock(ws.container_name):
            # Re-check under the lock in case the user came back meanwhile.
            session.refresh(ws)
            if ws.last_active_at >= older_than:
                continue
            try:
                running[ws.container_name].stop(timeout=5)
                stopped.append(ws.container_name)
            except NotFound:
                pass
            try:
                services.stop_services(get_lab(ws.lab_id), ws)  # the group stops as one unit
            except HTTPException:
                pass  # the lab no longer exists
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
