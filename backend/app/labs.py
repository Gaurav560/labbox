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


# Named resource tiers (v2 spec 4.6). A lab may say `resources: s` instead of numbers.
TIERS: dict[str, dict] = {
    "xs": {"cpus": 0.5, "memory": "512m", "pids_limit": 256},
    "s": {"cpus": 1, "memory": "1g", "pids_limit": 512},
    "m": {"cpus": 2, "memory": "2g", "pids_limit": 1024},
    "l": {"cpus": 2, "memory": "4g", "pids_limit": 1024},
}
SERVICE_NAME_RE = re.compile(r"^[a-z][a-z0-9-]{0,30}$")
RESERVED_SERVICE_NAMES = {"workspace", "gateway", "checker"}
# Extra capabilities a service may ask for (only when it runs as the image's own user).
SERVICE_CAPS = {"CHOWN", "SETUID", "SETGID", "FOWNER", "DAC_OVERRIDE"}
CHECKER_IMAGE = "labbox/checker:v1"
COVER_TYPES = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
COVER_MAX_BYTES = 512 * 1024


class WorkspaceConfig(_Strict):
    mount_path: str = "/workspace"
    shell: str = "/bin/bash"
    # bridge: normal Docker network with internet. lab: only the private per-user network.
    network: Literal["bridge", "none", "lab"] = "bridge"
    network_egress: bool = False  # with network: lab, also allow the internet
    env: dict[str, str] = {}  # extra environment for the workspace (e.g. PGHOST=db)
    sudo: bool = False  # v2, Phase F


class CheckConfig(_Strict):
    command: list[str] = Field(min_length=1)
    timeout_seconds: int = Field(default=30, gt=0, le=300)
    network: Literal["none"] = "none"  # never the internet
    # fresh: tests run on a copy of the learner's files. live: a checker container inspects the
    # running system on the lab network, and never runs the learner's code.
    mode: Literal["fresh", "live"] = "fresh"
    image: str | None = None  # live mode: checker image (default labbox/checker:v1)
    mount_workspace: Literal["ro"] | None = None  # live mode: also mount the learner's files read-only


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


class CoverCredit(_Strict):
    """Who took the cover photo (stock photo licenses do not require it, but we credit anyway)."""

    by: str
    url: str = ""  # link to the original (stock photos); empty for generated art
    source: str = "Pexels"


class ServiceResources(_Strict):
    cpus: float = Field(default=0.5, gt=0, le=8)
    memory: str = "256m"
    pids_limit: int = Field(default=256, gt=0, le=4096)

    @field_validator("memory")
    @classmethod
    def memory_format(cls, v: str) -> str:
        if not MEMORY_RE.match(v):
            raise ValueError("memory must look like 512m or 1g")
        return v


class Service(_Strict):
    """An extra container in the lab (a database, a cache...), reachable from the workspace by name."""

    name: str
    image: str
    env: dict[str, str] = {}
    resources: ServiceResources = ServiceResources()
    # "1000:1000" (default) runs as the learner's uid with no capabilities at all.
    # "default" keeps the image's own user; only then may cap_add list a few capabilities.
    user: str = "1000:1000"
    cap_add: list[str] = []
    command: list[str] | None = None
    data: str | None = None  # path inside the service kept across restarts (e.g. /var/lib/postgresql/data)
    ready: list[str] | None = None  # command that exits 0 once the service accepts connections

    @field_validator("name")
    @classmethod
    def name_format(cls, v: str) -> str:
        if not SERVICE_NAME_RE.match(v) or v in RESERVED_SERVICE_NAMES:
            raise ValueError(f"bad service name {v!r}: lowercase, digits and dashes, not {sorted(RESERVED_SERVICE_NAMES)}")
        return v

    @model_validator(mode="after")
    def caps_only_for_image_user(self) -> "Service":
        bad = set(self.cap_add) - SERVICE_CAPS
        if bad:
            raise ValueError(f"cap_add may only use {sorted(SERVICE_CAPS)}, not {sorted(bad)}")
        if self.cap_add and self.user != "default":
            raise ValueError("cap_add is only allowed with user: default")
        return self


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
    # Runs once, as root, when a learner first opens the chapter (failure injection, seed data).
    # The script lives in the image under /lab/setup/, never in /workspace.
    setup: list[str] | None = None
    setup_target: str = "workspace"  # or a service name
    # root (default) or learner. Lab containers drop every capability, so root cannot write the
    # learner's files; setups that build files in /workspace (a git repo, say) run as the learner.
    setup_user: Literal["root", "learner"] = "root"


class LabConfig(_Strict):
    id: str
    title: str
    description: str = ""  # v1 required it; v2 labs may use subtitle instead
    language: str = ""
    image: str = Field(min_length=1)
    resources: Resources  # numbers, or a tier name (xs, s, m, l) turned into numbers on load
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
    cover: str | None = None  # optional cover image in the lab folder; otherwise the UI draws one
    cover_credit: CoverCredit | None = None
    cover_scene: str | None = None  # what the generated cover shows (labbox cover --generate)
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

    @field_validator("resources", mode="before")
    @classmethod
    def tier_to_numbers(cls, v):
        if isinstance(v, str):
            if v not in TIERS:
                raise ValueError(f"unknown tier {v!r}: use one of {', '.join(TIERS)}")
            return TIERS[v]
        return v

    @model_validator(mode="after")
    def lab_network_rules(self) -> "LabConfig":
        names = [s.name for s in self.services]
        if len(names) != len(set(names)):
            raise ValueError("duplicate service names")
        if self.check.mode == "live" and not self.uses_lab_network:
            raise ValueError("check.mode: live needs services or workspace.network: lab")
        if self.check.mount_workspace and self.check.mode != "live":
            raise ValueError("check.mount_workspace is only for check.mode: live")
        if self.workspace.network_egress and self.workspace.network != "lab":
            raise ValueError("workspace.network_egress only applies to workspace.network: lab")
        if self.preview and self.workspace.network == "none" and not self.uses_lab_network:
            raise ValueError("preview needs a network (workspace.network: bridge or lab)")
        for c in self.chapters:
            if c.setup and c.setup_target != "workspace" and c.setup_target not in names:
                raise ValueError(f"chapter {c.id}: setup_target {c.setup_target!r} is not a service")
        return self

    @property
    def uses_lab_network(self) -> bool:
        """A private per-user network: for services, network: lab, live checks and the LLM relay."""
        return bool(self.services) or self.workspace.network == "lab" or self.llm.enabled

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
    if lab.resources.disk_mb is not None:
        found.append(("resources.disk_mb", "H"))
    if lab.workspace.sudo:
        found.append(("workspace.sudo", "F"))
    if lab.runtime != "default":
        found.append((f"runtime: {lab.runtime}", "F"))
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
        raise LabError(f"{yaml_path}: uses features this LabBox version does not have yet: {'; '.join(missing)}")
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
    if lab.cover:
        cover = (root / lab.cover).resolve()
        if root not in cover.parents or not cover.is_file():
            raise LabError(f"{yaml_path}: cover image missing: {lab.cover}")
        if cover.suffix.lower() not in COVER_TYPES:
            raise LabError(f"{yaml_path}: cover must be one of {', '.join(sorted(COVER_TYPES))}")
        if cover.stat().st_size > COVER_MAX_BYTES:
            raise LabError(f"{yaml_path}: cover is larger than {COVER_MAX_BYTES // 1024} KB")
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
