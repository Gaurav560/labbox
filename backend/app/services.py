"""Per-user lab networks and service containers (databases, caches...). v2 spec section 4.1.

A lab with services gets a private Docker network, labnet-u{user}-{lab}, with no internet
(unless the lab asks for it). Each service is a container on it that the workspace reaches by
the service name (db:5432). Everything here is blocking: call it via asyncio.to_thread.
"""
import logging
import shutil
import time
from pathlib import Path
from typing import Literal

from docker.errors import APIError, NotFound
from docker.models.containers import Container
from docker.models.networks import Network
from fastapi import HTTPException

from . import workspace_files
from .config import get_settings
from .labs import LabConfig, Service
from .models import Workspace

log = logging.getLogger(__name__)

READY_TIMEOUT_SECONDS = 90
READY_POLL_SECONDS = 0.5
WORKSPACE_ALIAS = "workspace"  # how services and the live checker reach the workspace

ServiceState = Literal["running", "starting", "stopped", "missing"]


def _client():
    from .containers import client  # containers imports this module

    return client()


def _labels(kind: str, ws: Workspace, extra: dict[str, str] | None = None) -> dict[str, str]:
    return {"labbox": "true", "labbox.kind": kind, "labbox.user": str(ws.user_id), "labbox.lab": ws.lab_id, **(extra or {})}


def network_name(ws: Workspace) -> str:
    return f"labnet-u{ws.user_id}-{ws.lab_id}"


def service_container_name(ws: Workspace, svc: Service) -> str:
    return f"{ws.container_name}-{svc.name}"


def data_dir(ws: Workspace, svc: Service) -> Path:
    """Next to the workspace folder, not inside it: database files never show up in /workspace."""
    return Path(f"{ws.volume_path}.services") / svc.name


def _get(name: str) -> Container | None:
    try:
        return _client().containers.get(name)
    except NotFound:
        return None


# ---------- network ----------


def ensure_network(lab: LabConfig, ws: Workspace) -> Network | None:
    if not lab.uses_lab_network:
        return None
    name = network_name(ws)
    try:
        return _client().networks.get(name)
    except NotFound:
        pass
    internal = not (lab.workspace.network == "lab" and lab.workspace.network_egress)
    try:
        net = _client().networks.create(name, driver="bridge", internal=internal, labels=_labels("network", ws))
        log.info("Created network %s (internal=%s)", name, internal)
        return net
    except APIError as e:
        if e.status_code == 409:  # created by another request at the same moment
            return _client().networks.get(name)
        raise


def networking_config(ws: Workspace, alias: str) -> dict:
    return {network_name(ws): _client().api.create_endpoint_config(aliases=[alias])}


def attach(container: Container, ws: Workspace, alias: str) -> None:
    """Connect an existing container to the lab network (idempotent)."""
    net = _client().networks.get(network_name(ws))
    container.reload()
    if network_name(ws) in container.attrs["NetworkSettings"]["Networks"]:
        return
    net.connect(container, aliases=[alias])


# ---------- services ----------


def _create_service(lab: LabConfig, ws: Workspace, svc: Service) -> Container:
    volumes = {}
    if svc.data:
        folder = data_dir(ws, svc)
        folder.mkdir(parents=True, exist_ok=True)
        workspace_files.chown(folder.parent)
        workspace_files.chown(folder)
        volumes[str(folder)] = {"bind": svc.data, "mode": "rw"}
    c = _client().containers.run(
        image=svc.image,
        name=service_container_name(ws, svc),
        detach=True,
        labels=_labels("service", ws, {"labbox.service": svc.name}),
        hostname=svc.name,
        network=network_name(ws),
        networking_config=networking_config(ws, svc.name),
        environment=svc.env,
        command=svc.command,
        user=None if svc.user == "default" else svc.user,
        cap_drop=["ALL"],
        cap_add=svc.cap_add or None,
        security_opt=["no-new-privileges:true"],
        nano_cpus=int(svc.resources.cpus * 1e9),
        mem_limit=svc.resources.memory,
        memswap_limit=svc.resources.memory,
        pids_limit=svc.resources.pids_limit,
        volumes=volumes,
        runtime=get_settings().CONTAINER_RUNTIME or None,
    )
    log.info("Created service %s from %s", c.name, svc.image)
    return c


def _wait_ready(lab: LabConfig, ws: Workspace) -> None:
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    for svc in lab.services:
        if not svc.ready:
            continue
        while True:
            c = _get(service_container_name(ws, svc))
            if c is not None:
                c.reload()
                if c.status == "exited":
                    logs = c.logs(tail=20).decode(errors="replace")
                    raise HTTPException(500, f"Service {svc.name} stopped while starting:\n{logs}")
                try:
                    if c.exec_run(svc.ready, user=None if svc.user == "default" else svc.user).exit_code == 0:
                        break
                except APIError:
                    pass  # not running yet
            if time.monotonic() > deadline:
                raise HTTPException(500, f"Service {svc.name} did not become ready in {READY_TIMEOUT_SECONDS} s")
            time.sleep(READY_POLL_SECONDS)


def ensure_services(lab: LabConfig, ws: Workspace) -> None:
    """Network up, every service created and running, and ready (call before the workspace starts)."""
    ensure_network(lab, ws)
    for svc in lab.services:
        c = _get(service_container_name(ws, svc))
        if c is None:
            _create_service(lab, ws, svc)
        elif c.status != "running":
            c.start()
            log.info("Started service %s", c.name)
    _wait_ready(lab, ws)


def stop_services(lab: LabConfig, ws: Workspace) -> None:
    for svc in lab.services:
        c = _get(service_container_name(ws, svc))
        if c is not None and c.status == "running":
            c.stop(timeout=10)  # databases get time to shut down cleanly
            log.info("Stopped service %s", c.name)


def remove_services(lab: LabConfig, ws: Workspace, wipe_data: bool) -> None:
    """Used by reset: containers go, and with wipe_data their data folders too."""
    for svc in lab.services:
        c = _get(service_container_name(ws, svc))
        if c is not None:
            c.remove(force=True)
        if wipe_data and svc.data:
            shutil.rmtree(data_dir(ws, svc), ignore_errors=True)


def service_states(lab: LabConfig, ws: Workspace) -> list[dict]:
    out = []
    for svc in lab.services:
        c = _get(service_container_name(ws, svc))
        state: ServiceState = "missing" if c is None else "running" if c.status == "running" else "stopped"
        out.append({"name": svc.name, "status": state})
    return out


def container_ip(name: str, prefer_network: str | None = None) -> str | None:
    """IP of a running container, on the lab network if it has one (used by the preview proxy)."""
    c = _get(name)
    if c is None or c.status != "running":
        return None
    nets: dict = c.attrs["NetworkSettings"]["Networks"]
    if prefer_network and nets.get(prefer_network, {}).get("IPAddress"):
        return nets[prefer_network]["IPAddress"]
    for n in nets.values():
        if n.get("IPAddress"):
            return n["IPAddress"]
    return None
