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

from . import containers, progress, workspace_files
from .config import get_settings
from .labs import LabConfig
from .models import CheckRun, User, Workspace

log = logging.getLogger(__name__)

RESULT_PREFIX = "@@RESULT "
METRIC_PREFIX = "@@METRIC "
MAX_METRICS = 20
OUTPUT_TAIL_CHARS = 4000
MAX_COPY_BYTES = 20 * 1024 * 1024
CHECK_PIDS_LIMIT = 128
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


class _RawResult(BaseModel):
    task: str
    passed: bool
    message: str = ""
    expected: str | int | float | None = None
    actual: str | int | float | None = None


# ---------- one check per user at a time ----------

_running: set[int] = set()
_running_lock = asyncio.Lock()


@asynccontextmanager
async def check_slot(user_id: int) -> AsyncIterator[None]:
    async with _running_lock:
        if user_id in _running:
            raise HTTPException(429, "A check is already running")
        _running.add(user_id)
    try:
        yield
    finally:
        async with _running_lock:
            _running.discard(user_id)


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


def _run_container(lab: LabConfig, user_id: int, tmp: Path) -> tuple[str, bool]:
    """Returns (logs, timed_out)."""
    short = uuid.uuid4().hex[:8]
    c = containers.client().containers.run(
        image=lab.image,
        name=f"check-u{user_id}-{lab.id}-{short}",
        command=lab.check.command,
        detach=True,
        labels=containers.labels("check", user_id, lab.id),
        working_dir="/check/workspace",
        volumes={
            str(tmp / "workspace"): {"bind": "/check/workspace", "mode": "rw"},
            str(tmp / "tests"): {"bind": "/check/tests", "mode": "ro"},
        },
        network_mode="none",
        pids_limit=CHECK_PIDS_LIMIT,
        environment={"HOME": "/tmp", "PYTHONDONTWRITEBYTECODE": "1"},
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


def check_folder(lab: LabConfig, chapter_id: str, folder: Path, user_id: int) -> CheckResponse:
    """Run the chapter's hidden tests against a copy of `folder` in a throwaway container.

    Used for every Check (folder = the user's workspace) and by `labbox test-lab`
    (folder = starter/ or solution/), so both always grade the same way.
    """
    chapter = lab.chapter(chapter_id)  # 404 if unknown
    tmp = get_settings().CHECKS_DIR / uuid.uuid4().hex
    started = time.monotonic()
    try:
        copy_workspace(folder, tmp / "workspace")
        shutil.copytree(lab.tests_dir, tmp / "tests", symlinks=True)
        workspace_files.chown_tree(tmp)
        logs, timed_out = _run_container(lab, user_id, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    duration_ms = int((time.monotonic() - started) * 1000)

    if timed_out:
        msg = f"Timed out after {lab.check.timeout_seconds} seconds (infinite loop?)"
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


def run_check(session: Session, user: User, lab: LabConfig, chapter_id: str) -> CheckResponse:
    assert user.id is not None
    lab.chapter(chapter_id)  # 404 if unknown
    ws: Workspace = containers.get_workspace(session, user, lab)
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
    progress.record_check(session, user.id, lab.id, chapter_id, {r.task: r.passed for r in res.results})
    log.info(
        "Check user=%s lab=%s chapter=%s: %d/%d passed in %d ms%s",
        user.id, lab.id, chapter_id, res.passed_count, res.total_count, res.duration_ms, " (timed out)" if res.timed_out else "",
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
