"""Content next to the labs: skill maps (tracks/), daily drills (drills/) and onboarding.

Loaded and validated at start-up like the labs: a broken file stops the backend with a clear error.
"""
import logging
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .labs import LabError, Track, all_labs

log = logging.getLogger(__name__)


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Choice(_Strict):
    """A server-checked multiple choice question (drills and placement)."""

    question: str
    options: list[str] = Field(min_length=2, max_length=6)
    answer: int
    explain: str = ""

    @model_validator(mode="after")
    def answer_in_range(self) -> "Choice":
        if not 0 <= self.answer < len(self.options):
            raise ValueError(f"answer {self.answer} is not one of the {len(self.options)} options")
        return self


class SkillNode(_Strict):
    id: str
    title: str
    requires: list[str] = []
    chapters: list[str] = []  # "lab-id/chapter-id"


class TrackMap(_Strict):
    track: Track
    title: str
    nodes: list[SkillNode] = Field(min_length=1)


class Drill(Choice):
    id: str
    kind: Literal["predict", "bug", "command"]


class DrillFile(_Strict):
    track: Track
    drills: list[Drill]


class Goal(_Strict):
    id: str
    title: str
    blurb: str
    track: Track
    start: list[str] = Field(min_length=1)  # lab ids, first existing one wins


class Onboarding(_Strict):
    goals: list[Goal] = Field(min_length=1)
    placement: list[Choice] = Field(min_length=1, max_length=5)


class Content(BaseModel):
    tracks: dict[str, TrackMap] = {}
    drills: list[tuple[str, Drill]] = []  # (track, drill)
    onboarding: Onboarding | None = None


def _read(path: Path, model: type[BaseModel]):
    try:
        return model.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    except (OSError, yaml.YAMLError, ValidationError) as e:
        raise LabError(f"{path}: invalid:\n{e}") from e


def _check_track(path: Path, t: TrackMap, chapters: set[str]) -> None:
    ids = [n.id for n in t.nodes]
    if len(ids) != len(set(ids)):
        raise LabError(f"{path}: duplicate node ids")
    by_id = {n.id: n for n in t.nodes}
    for n in t.nodes:
        for r in n.requires:
            if r not in by_id:
                raise LabError(f"{path}: node {n.id!r} requires unknown node {r!r}")
        for c in n.chapters:
            if c not in chapters:
                raise LabError(f"{path}: node {n.id!r} refers to unknown chapter {c!r} (use lab-id/chapter-id)")
    # No cycles: every node must be reachable by repeatedly taking nodes whose requirements are done.
    done: set[str] = set()
    while len(done) < len(ids):
        ready = [n.id for n in t.nodes if n.id not in done and set(n.requires) <= done]
        if not ready:
            raise LabError(f"{path}: the requires links form a loop")
        done |= set(ready)


def load_content(root: Path) -> Content:
    """root is the folder holding labs/, tracks/, drills/ and onboarding/."""
    chapters = {f"{lab.id}/{c.id}" for lab in all_labs() for c in lab.chapters}
    lab_ids = {lab.id for lab in all_labs()}
    content = Content()
    for path in sorted((root / "tracks").glob("*.yaml")):
        t = _read(path, TrackMap)
        _check_track(path, t, chapters)
        if t.track in content.tracks:
            raise LabError(f"{path}: track {t.track!r} already has a skill map")
        content.tracks[t.track] = t
    seen: set[str] = set()
    for path in sorted((root / "drills").glob("*.yaml")):
        f = _read(path, DrillFile)
        for d in f.drills:
            if d.id in seen:
                raise LabError(f"{path}: duplicate drill id {d.id!r}")
            seen.add(d.id)
            content.drills.append((f.track, d))
    ob = root / "onboarding" / "onboarding.yaml"
    if ob.is_file():
        content.onboarding = _read(ob, Onboarding)
        for g in content.onboarding.goals:
            if not any(s in lab_ids for s in g.start):
                raise LabError(f"{ob}: goal {g.id!r} starts with none of the existing labs ({', '.join(g.start)})")
    log.info("Loaded %d skill maps, %d drills, onboarding: %s", len(content.tracks), len(content.drills), bool(content.onboarding))
    return content


_content = Content()


def init_content(root: Path) -> None:
    global _content
    _content = load_content(root)


def get_content() -> Content:
    return _content
