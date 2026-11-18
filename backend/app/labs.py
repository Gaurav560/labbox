"""Load and validate labs/*/lab.yaml into LabConfig objects."""
import logging
import re
from pathlib import Path
from typing import Literal

import yaml
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from .lessons import LessonError, Step, parse_steps

log = logging.getLogger(__name__)

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TASK_ID_RE = re.compile(r"^[a-z0-9_]+$")
MEMORY_RE = re.compile(r"^\d+[kmg]$")


class LabError(Exception):
    pass


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Resources(_Strict):
    cpus: float = Field(gt=0, le=8)
    memory: str
    pids_limit: int = Field(gt=0, le=4096)
    disk_mb: int | None = Field(default=None, gt=0)  # v2, needs disk quotas (Phase H)

    @field_validator("memory")
    @classmethod
    def memory_format(cls, v: str) -> str:
        if not MEMORY_RE.match(v):
            raise ValueError("memory must look like 512m or 1g")
        return v


class WorkspaceConfig(_Strict):
    mount_path: str = "/workspace"
    shell: str = "/bin/bash"
    network: Literal["bridge", "none", "lab"] = "bridge"  # "lab": private per-user network (Phase D)
    network_egress: bool = False  # v2, Phase D
    sudo: bool = False  # v2, Phase F


class CheckConfig(_Strict):
    command: list[str] = Field(min_length=1)
    timeout_seconds: int = Field(default=30, gt=0, le=300)
    network: Literal["none"] = "none"
    mode: Literal["fresh", "live"] = "fresh"  # v2: "live" checks the running system (Phase D)
    mount_workspace: Literal["ro"] | None = None  # v2, live mode only (Phase D)


# ---------- v2 lab fields (all optional) ----------

Track = Literal["languages", "frameworks", "databases", "devops", "system-design", "ai", "interview"]


class Character(_Strict):
    name: str
    role: str = ""
    avatar: str | None = None


class Story(_Strict):
    company: str = ""
    character: Character | None = None
    pitch: str = ""


class ServiceResources(_Strict):
    cpus: float = Field(default=0.5, gt=0, le=8)
    memory: str = "256m"


class Service(_Strict):
    name: str
    image: str
    env: dict[str, str] = {}
    resources: ServiceResources | None = None
    user: str | None = None


class PreviewPort(_Strict):
    name: str
    port: int = Field(gt=0, lt=65536)
    path: str = "/"


class LLMConfig(_Strict):
    enabled: bool = False


class Task(_Strict):
    id: str
    title: str
    xp: int = Field(default=20, ge=0, le=1000)
    # Hint ladder: a nudge, a direction, then almost there (never the full solution).
    hints: list[str] = Field(default=[], max_length=3)

    @field_validator("id")
    @classmethod
    def id_format(cls, v: str) -> str:
        if not TASK_ID_RE.match(v):
            raise ValueError(f"bad task id {v!r}: use a-z, 0-9 and _")
        return v


class Chapter(_Strict):
    id: str
    title: str
    file: str
    tasks: list[Task] = Field(min_length=1)
    minutes: int | None = Field(default=None, gt=0)
    setup: list[str] | None = None  # v2: failure injection script (Phase D)
    setup_target: str | None = None


class LabConfig(_Strict):
    id: str
    title: str
    description: str = ""  # v1 required it; v2 labs may use subtitle instead
    language: str = ""
    image: str = Field(min_length=1)
    resources: Resources | Literal["xs", "s", "m", "l"]  # v2: a tier name (Phase D)
    workspace: WorkspaceConfig = WorkspaceConfig()
    check: CheckConfig
    chapters: list[Chapter] = Field(min_length=1)

    # v2 fields. Defaults keep v1 files working unchanged.
    version: Literal[1, 2] = 1
    subtitle: str = ""
    track: Track = "languages"
    tags: list[str] = []
    level: Literal["beginner", "intermediate", "advanced"] | None = None
    estimated_minutes: int | None = Field(default=None, gt=0)
    free_chapters: int = Field(default=2, ge=0)
    prerequisites: list[str] = []  # other lab ids, a recommendation only
    story: Story | None = None
    runtime: Literal["default", "gvisor", "sysbox"] = "default"
    services: list[Service] = []
    preview: list[PreviewPort] = []
    llm: LLMConfig = LLMConfig()

    # Set by the loader, not read from YAML.
    root: Path = Field(default=Path("."), exclude=True)

    @field_validator("id")
    @classmethod
    def id_format(cls, v: str) -> str:
        if not ID_RE.match(v):
            raise ValueError(f"bad lab id {v!r}: lowercase a-z, 0-9 and dashes only")
        return v

    @model_validator(mode="after")
    def fill_v1_fields(self) -> "LabConfig":
        if not self.description:
            self.description = self.subtitle
        if not self.language and self.tags:
            self.language = self.tags[0]
        return self

    @model_validator(mode="after")
    def unique_ids(self) -> "LabConfig":
        chapter_ids = [c.id for c in self.chapters]
        if len(chapter_ids) != len(set(chapter_ids)):
            raise ValueError("duplicate chapter ids")
        task_ids = [t.id for c in self.chapters for t in c.tasks]
        dupes = sorted({t for t in task_ids if task_ids.count(t) > 1})
        if dupes:
            raise ValueError(f"duplicate task ids: {', '.join(dupes)}")
        return self

    @property
    def starter_dir(self) -> Path:
        return self.root / "starter"

    @property
    def tests_dir(self) -> Path:
        return self.root / "tests"

    @property
    def task_count(self) -> int:
        return sum(len(c.tasks) for c in self.chapters)

    def chapter(self, chapter_id: str) -> Chapter:
        for c in self.chapters:
            if c.id == chapter_id:
                return c
        raise HTTPException(404, f"Chapter {chapter_id!r} not found")

    def chapter_markdown(self, chapter_id: str) -> str:
        return (self.root / self.chapter(chapter_id).file).read_text(encoding="utf-8")

    def chapter_steps(self, chapter_id: str) -> list[Step]:
        return parse_steps(self.chapter_markdown(chapter_id))

    def task(self, chapter_id: str, task_id: str) -> Task:
        for t in self.chapter(chapter_id).tasks:
            if t.id == task_id:
                return t
        raise HTTPException(404, f"Task {task_id!r} not found in chapter {chapter_id!r}")


def unsupported_features(lab: LabConfig) -> list[str]:
    """v2 fields whose engine is not built yet. Refusing them beats silently ignoring them."""
    found: list[tuple[str, str]] = []
    if isinstance(lab.resources, str):
        found.append(("resources tiers (xs, s, m, l)", "D"))
    elif lab.resources.disk_mb is not None:
        found.append(("resources.disk_mb", "H"))
    if lab.workspace.network == "lab" or lab.workspace.network_egress:
        found.append(("workspace.network: lab", "D"))
    if lab.workspace.sudo:
        found.append(("workspace.sudo", "F"))
    if lab.check.mode == "live" or lab.check.mount_workspace:
        found.append(("check.mode: live", "D"))
    if lab.services:
        found.append(("services", "D"))
    if lab.preview:
        found.append(("preview", "D"))
    if lab.llm.enabled:
        found.append(("llm", "E"))
    if lab.runtime != "default":
        found.append((f"runtime: {lab.runtime}", "F"))
    if any(c.setup or c.setup_target for c in lab.chapters):
        found.append(("chapter setup", "D"))
    return [f"{name} needs Phase {phase} (not built yet)" for name, phase in found]


def load_lab(folder: Path) -> LabConfig:
    yaml_path = folder / "lab.yaml"
    try:
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        raise LabError(f"{yaml_path}: cannot read: {e}") from e
    if not isinstance(raw, dict):
        raise LabError(f"{yaml_path}: must be a mapping")
    try:
        lab = LabConfig(**raw)
    except ValidationError as e:
        raise LabError(f"{yaml_path}: invalid:\n{e}") from e

    if lab.id != folder.name:
        raise LabError(f"{yaml_path}: id {lab.id!r} must equal folder name {folder.name!r}")
    missing = unsupported_features(lab)
    if missing:
        raise LabError(f"{yaml_path}: uses features this LabBox does not have yet: {'; '.join(missing)}")
    root = folder.resolve()
    for ch in lab.chapters:
        chapter_file = (root / ch.file).resolve()
        if root not in chapter_file.parents or not chapter_file.is_file():
            raise LabError(f"{yaml_path}: chapter file missing: {ch.file}")
        try:
            steps = parse_steps(chapter_file.read_text(encoding="utf-8"))
        except LessonError as e:
            raise LabError(f"{ch.file}: {e}") from e
        task_ids = {t.id for t in ch.tasks}
        for s in steps:
            if s.task and s.task not in task_ids:
                raise LabError(f"{ch.file}: step refers to task {s.task!r}, which is not a task of chapter {ch.id!r}")
    if not (root / "tests").is_dir():
        raise LabError(f"{yaml_path}: tests/ folder missing")
    lab.root = root
    return lab


def load_labs(labs_dir: Path) -> dict[str, LabConfig]:
    if not labs_dir.is_dir():
        raise LabError(f"LABS_DIR {labs_dir} does not exist")
    labs: dict[str, LabConfig] = {}
    for folder in sorted(p for p in labs_dir.iterdir() if p.is_dir()):
        if not (folder / "lab.yaml").exists():
            continue
        lab = load_lab(folder)
        labs[lab.id] = lab
    if not labs:
        raise LabError(f"No labs found in {labs_dir}")
    log.info("Loaded %d labs: %s", len(labs), ", ".join(labs))
    return labs


_registry: dict[str, LabConfig] = {}


def init_labs(labs_dir: Path) -> None:
    global _registry
    _registry = load_labs(labs_dir)


def all_labs() -> list[LabConfig]:
    return list(_registry.values())


def get_lab(lab_id: str) -> LabConfig:
    lab = _registry.get(lab_id)
    if lab is None:
        raise HTTPException(404, f"Lab {lab_id!r} not found")
    return lab
