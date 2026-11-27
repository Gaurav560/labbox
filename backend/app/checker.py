"""Runs hidden tests in a throwaway container and tracks task progress."""
import asyncio
import json
import logging
import os
import shutil
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, ValidationError
from sqlmodel import Session, col, select

from . import containers, engagement, progress, services, shared, workspace_files
from .certificates import CheckCertificate
from .config import get_settings
from .labs import CHECKER_IMAGE, LabConfig
from .models import CheckRun, User, Workspace

log = logging.getLogger(__name__)

RESULT_PREFIX = "@@RESULT "
METRIC_PREFIX = "@@METRIC "
MAX_METRICS = 20
OUTPUT_TAIL_CHARS = 4000
MAX_COPY_BYTES = 20 * 1024 * 1024
CHECK_PIDS_LIMIT = 1024  # upper bound; a check gets min(this, the lab's own pids_limit)
NO_RESULT = "No result reported (did your code crash?)"


class TaskResult(BaseModel):
    task: str
    title: str = ""
    passed: bool
    message: str
    expected: str | None = None
    actual: str | None = None


class Metric(BaseModel):
    """Optional v2 line, e.g. latency for performance labs: @@METRIC {"name": "p95_ms", "value": 180}."""

    name: str
    value: float
    target: float | None = None
    better: Literal["lower", "higher"] | None = None


class CheckResponse(BaseModel):
    passed_count: int
    total_count: int
    results: list[TaskResult]
    output: str
    duration_ms: int
    metrics: list[Metric] = []
    timed_out: bool = False
    xp_awarded: list[engagement.XpAward] = []
    # Set when this check finished the lab (80% of its tasks): the certificate issued, or a prompt to claim it.
    certificate: CheckCertificate | None = None


class _RawResult(BaseModel):
    task: str
    passed: bool
    message: str = ""
    expected: str | int | float | None = None
    actual: str | int | float | None = None


# ---------- one check per user at a time ----------

# A check never takes longer than this (the lab's own timeout is at most 300 s); if a worker dies
# mid-check, the learner's slot frees itself after it.
CHECK_SLOT_SECONDS = 15 * 60


@asynccontextmanager
async def check_slot(user_id: int) -> AsyncIterator[None]:
    """One check per learner at a time, across every worker (shared.claim)."""
    key = f"check:{user_id}"
    token = await asyncio.to_thread(shared.claim, key, CHECK_SLOT_SECONDS)
    if token is None:
        raise HTTPException(429, "A check is already running")
    try:
        yield
    finally:
        await asyncio.to_thread(shared.release, key, token)


# ---------- preparing the throwaway copy ----------


def copy_workspace(src: Path, dst: Path) -> None:
    """Copy the user's files, skipping ignored folders and never following symlinks. Caps total size."""
    total = 0
    src = src.resolve()
    for dirpath, dirnames, filenames in os.walk(src, followlinks=False):
        dirnames[:] = [d for d in dirnames if not workspace_files.is_ignored(d)]
        here = Path(dirpath)
        out_dir = dst / here.relative_to(src)
        out_dir.mkdir(parents=True, exist_ok=True)
        for d in dirnames:
            if (here / d).is_symlink():
                os.symlink(os.readlink(here / d), out_dir / d)
        for name in filenames:
            if workspace_files.is_ignored(name):
                continue
            p = here / name
            if p.is_symlink():
                # Copy the link itself. Inside the check container it can only point at that container's files.
                os.symlink(os.readlink(p), out_dir / name)
                continue
            if not p.is_file():
                continue
            total += p.stat().st_size
            if total > MAX_COPY_BYTES:
                raise HTTPException(413, "Your workspace is larger than 20 MB, delete some files and try again")
            shutil.copyfile(p, out_dir / name, follow_symlinks=False)


# ---------- parsing ----------


def parse_results(logs: str, lab: LabConfig, chapter_id: str) -> list[TaskResult]:
    reported: dict[str, _RawResult] = {}
    for line in logs.splitlines():
        if not line.startswith(RESULT_PREFIX):
            continue
        try:
            r = _RawResult.model_validate_json(line[len(RESULT_PREFIX):])
        except ValidationError:
            continue
        prev = reported.get(r.task)
        # Any failure wins, so user code printing a fake "passed" line cannot hide a real failure.
        if prev is None or (prev.passed and not r.passed):
            reported[r.task] = r
    results = []
    for task in lab.chapter(chapter_id).tasks:
        r = reported.get(task.id)
        if r is None:
            results.append(TaskResult(task=task.id, title=task.title, passed=False, message=NO_RESULT))
        else:
            results.append(
                TaskResult(
                    task=task.id,
                    title=task.title,
                    passed=r.passed,
                    message=r.message[:500],
                    expected=None if r.expected is None else str(r.expected)[:500],
                    actual=None if r.actual is None else str(r.actual)[:500],
                )
            )
    return results


def parse_metrics(logs: str) -> list[Metric]:
    """@@METRIC lines; a name reported twice keeps its last value."""
    found: dict[str, Metric] = {}
    for line in logs.splitlines():
        if not line.startswith(METRIC_PREFIX):
            continue
        try:
            m = Metric.model_validate_json(line[len(METRIC_PREFIX):])
        except ValidationError:
            continue
        m.name = m.name[:64]
        if m.name in found or len(found) < MAX_METRICS:
            found[m.name] = m
    return list(found.values())


# ---------- running ----------


def _run_container(lab: LabConfig, user_id: int, tmp: Path, live_ws: Workspace | None = None, chapter_id: str = "") -> tuple[str, bool]:
    """Returns (logs, timed_out).

    fresh: the lab image, the copied files in /check/workspace, no network at all.
    live: the checker image on the learner's lab network, tests only (the learner's files only
    read-only and only if the lab asks). No learner code ever runs in it, so it cannot be faked.
    """
    short = uuid.uuid4().hex[:8]
    volumes = {str(tmp / "tests"): {"bind": "/check/tests", "mode": "ro"}}
    if live_ws is None:
        volumes[str(tmp / "workspace")] = {"bind": "/check/workspace", "mode": "rw"}
        where = dict(image=lab.image, working_dir="/check/workspace", network_mode="none")
    else:
        if lab.check.mount_workspace:
            volumes[live_ws.volume_path] = {"bind": "/check/workspace", "mode": "ro"}
        where = dict(
            image=lab.check.image or CHECKER_IMAGE,
            working_dir="/check",
            network=services.network_name(live_ws),
            networking_config=services.networking_config(live_ws, "checker"),
        )
    c = containers.client().containers.run(
        name=f"check-{containers.instance_tag()}u{user_id}-{lab.id}-{short}",
        command=lab.check.command,
        detach=True,
        labels=containers.labels("check", user_id, lab.id),
        volumes=volumes,
        pids_limit=min(lab.resources.pids_limit, CHECK_PIDS_LIMIT),
        # LABBOX_CHAPTER and LABBOX_TASKS let a check script test only the chapter being checked (a big
        # course stays fast); scripts that ignore them run everything, as before.
        environment={
            "HOME": "/tmp", "PYTHONDONTWRITEBYTECODE": "1", "LABBOX_CHAPTER": chapter_id,
            "LABBOX_TASKS": ",".join(t.id for t in lab.chapter(chapter_id).tasks) if chapter_id else "",
        },
        **where,
        **containers.security_options(lab),
    )
    timed_out = False
    try:
        try:
            c.wait(timeout=lab.check.timeout_seconds)
        except Exception:  # requests ReadTimeout / ConnectionError
            timed_out = True
            try:
                c.kill()
            except Exception:
                pass
        logs = c.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
    finally:
        c.remove(force=True)
    return logs, timed_out


def _grade(lab: LabConfig, chapter_id: str, user_id: int, folder: Path | None = None, live_ws: Workspace | None = None) -> CheckResponse:
    chapter = lab.chapter(chapter_id)  # 404 if unknown
    tmp = get_settings().CHECKS_DIR / uuid.uuid4().hex
    started = time.monotonic()
    try:
        if folder is not None:
            copy_workspace(folder, tmp / "workspace")
        shutil.copytree(lab.tests_dir, tmp / "tests", symlinks=True)
        workspace_files.chown_tree(tmp)
        logs, timed_out = _run_container(lab, user_id, tmp, live_ws, chapter_id)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    duration_ms = int((time.monotonic() - started) * 1000)

    if timed_out:
        msg = f"Timed out after {lab.check.timeout_seconds} seconds" + ("" if live_ws else " (infinite loop?)")
        results = [TaskResult(task=t.id, title=t.title, passed=False, message=msg) for t in chapter.tasks]
    else:
        results = parse_results(logs, lab, chapter_id)
    return CheckResponse(
        passed_count=sum(r.passed for r in results),
        total_count=len(results),
        results=results,
        output=logs[-OUTPUT_TAIL_CHARS:],
        duration_ms=duration_ms,
        metrics=[] if timed_out else parse_metrics(logs),
        timed_out=timed_out,
    )


def check_folder(lab: LabConfig, chapter_id: str, folder: Path, user_id: int) -> CheckResponse:
    """fresh mode: run the chapter's hidden tests against a copy of `folder` in a throwaway container.

    Used for every Check (folder = the user's workspace) and by `labbox test-lab`
    (folder = starter/ or solution/), so both always grade the same way.
    """
    return _grade(lab, chapter_id, user_id, folder=folder)


def check_live(lab: LabConfig, chapter_id: str, ws: Workspace) -> CheckResponse:
    """live mode: a checker container inspects the learner's running group (services must be up)."""
    return _grade(lab, chapter_id, ws.user_id, live_ws=ws)


def run_check(session: Session, user: User, lab: LabConfig, chapter_id: str) -> CheckResponse:
    assert user.id is not None
    lab.chapter(chapter_id)  # 404 if unknown
    if lab.check.mode == "live":
        containers.get_workspace(session, user, lab, chapter_id)  # this chapter's starter folder is in (plan A)
        ws = containers.ensure_workspace(session, user, lab)  # the system must be running to be checked
        res = check_live(lab, chapter_id, ws)
    else:
        ws = containers.get_workspace(session, user, lab, chapter_id)
        containers.touch(session, ws)
        res = check_folder(lab, chapter_id, Path(ws.volume_path), user.id)

    session.add(
        CheckRun(
            user_id=user.id,
            lab_id=lab.id,
            chapter_id=chapter_id,
            passed_count=res.passed_count,
            total_count=res.total_count,
            results_json=json.dumps([r.model_dump(exclude={"title"}, exclude_none=True) for r in res.results]),
            output_tail=res.output,
            duration_ms=res.duration_ms,
        )
    )
    session.commit()
    passed = {r.task: r.passed for r in res.results}
    progress.record_check(session, user.id, lab.id, chapter_id, passed)
    res.xp_awarded = engagement.award_for_check(session, user.id, lab, chapter_id, passed)
    log.info(
        "Check user=%s lab=%s chapter=%s (%s): %d/%d passed in %d ms%s",
        user.id, lab.id, chapter_id, lab.check.mode, res.passed_count, res.total_count, res.duration_ms,
        " (timed out)" if res.timed_out else "",
    )
    return res


# ---------- history and progress ----------


class CheckRunOut(BaseModel):
    id: int
    chapter_id: str
    passed_count: int
    total_count: int
    results: list[TaskResult]
    duration_ms: int
    created_at: str


def recent_checks(session: Session, user_id: int, lab: LabConfig, limit: int) -> list[CheckRunOut]:
    runs = session.exec(
        select(CheckRun)
        .where(CheckRun.user_id == user_id, CheckRun.lab_id == lab.id)
        .order_by(col(CheckRun.id).desc())
        .limit(limit)
    ).all()
    return [
        CheckRunOut(
            id=r.id or 0,
            chapter_id=r.chapter_id,
            passed_count=r.passed_count,
            total_count=r.total_count,
            results=[TaskResult(**x) for x in json.loads(r.results_json)],
            duration_ms=r.duration_ms,
            created_at=r.created_at.isoformat() + "Z",
        )
        for r in runs
    ]


def task_states(session: Session, user_id: int, lab: LabConfig) -> dict[str, bool]:
    """Latest pass state per task id, from each chapter's most recent check run."""
    states: dict[str, bool] = {}
    for chapter in lab.chapters:
        run = session.exec(
            select(CheckRun)
            .where(CheckRun.user_id == user_id, CheckRun.lab_id == lab.id, CheckRun.chapter_id == chapter.id)
            .order_by(col(CheckRun.id).desc())
        ).first()
        if run is None:
            continue
        for r in json.loads(run.results_json):
            states[r["task"]] = bool(r["passed"])
    return states
