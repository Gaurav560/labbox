"""Load and validate labs/*/lab.yaml into LabConfig objects."""
import logging
import re
from pathlib import Path
from typing import Literal

import yaml
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

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

    @field_validator("memory")
    @classmethod
    def memory_format(cls, v: str) -> str:
        if not MEMORY_RE.match(v):
            raise ValueError("memory must look like 512m or 1g")
        return v


class WorkspaceConfig(_Strict):
    mount_path: str = "/workspace"
    shell: str = "/bin/bash"
    network: Literal["bridge", "none"] = "bridge"


class CheckConfig(_Strict):
    command: list[str] = Field(min_length=1)
    timeout_seconds: int = Field(default=30, gt=0, le=300)
    network: Literal["none"] = "none"


class Task(_Strict):
    id: str
    title: str

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


class LabConfig(_Strict):
    id: str
    title: str
    description: str
    language: str
    image: str = Field(min_length=1)
    resources: Resources
    workspace: WorkspaceConfig = WorkspaceConfig()
    check: CheckConfig
    chapters: list[Chapter] = Field(min_length=1)

    # Set by the loader, not read from YAML.
    root: Path = Field(default=Path("."), exclude=True)

    @field_validator("id")
    @classmethod
    def id_format(cls, v: str) -> str:
        if not ID_RE.match(v):
            raise ValueError(f"bad lab id {v!r}: lowercase a-z, 0-9 and dashes only")
        return v

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
    root = folder.resolve()
    for ch in lab.chapters:
        chapter_file = (root / ch.file).resolve()
        if root not in chapter_file.parents or not chapter_file.is_file():
            raise LabError(f"{yaml_path}: chapter file missing: {ch.file}")
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
