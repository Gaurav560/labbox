"""Where a chapter's code is: the file and line a lab opens when the learner switches chapters.

The learner's own copy is searched first (their edits move lines), then the starter files. In order:
a TODO naming one of the chapter's tasks (`TODO(price_cache)`, `TODO (task total)`), moved up to a
section header just above it (`# ---------- chapter 6 ...`); else a `chapter <n>` marker; else the
README; else the first TODO. Chapters done only in the terminal (Redis 1 to 4, say) land on the README.
"""

import re
from pathlib import Path

from .labs import Chapter, LabConfig

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "target", "build", "dist", ".mypy_cache"}
MAX_FILES = 400
MAX_BYTES = 300_000


def _files(root: Path) -> list[Path]:
    out: list[Path] = []
    if not root.is_dir():
        return out
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel.parts):
            continue
        if p.is_file() and p.stat().st_size <= MAX_BYTES:
            out.append(p)
            if len(out) >= MAX_FILES:
                break
    return out


def _lines(p: Path) -> list[str] | None:
    try:
        return p.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return None


def _find(root: Path, chapter: Chapter, number: int, any_todo: bool = False, task_ids: list[str] | None = None) -> tuple[str, int] | None:
    ids = "|".join(re.escape(t) for t in (task_ids if task_ids is not None else [t.id for t in chapter.tasks]))
    todo = re.compile(rf"TODO\s*\(\s*(?:task\s+)?(?:{ids})\b|\(\s*task\s+(?:{ids})\b")
    marker = re.compile(rf"\bchapter\s+{number}\b", re.IGNORECASE)
    header = re.compile(r"\bchapter\s+\d+\b", re.IGNORECASE)
    files = [(p, _lines(p)) for p in _files(root)]
    files = [(p, ls) for p, ls in files if ls is not None]
    for p, ls in files:
        for i, line in enumerate(ls):
            if todo.search(line):
                top = i
                for j in range(i - 1, max(-1, i - 8), -1):  # a section header right above it
                    if header.search(ls[j]):
                        top = j
                        break
                return str(p.relative_to(root)), top + 1
    for pattern in [re.compile(r"\bTODO\b")] if any_todo else [marker]:
        for p, ls in files:
            for i, line in enumerate(ls):
                if pattern.search(line):
                    return str(p.relative_to(root)), i + 1
    return None


def chapter_focus(lab: LabConfig, chapter: Chapter, folder: Path | None) -> tuple[str, int] | None:
    number = next(i for i, c in enumerate(lab.chapters, 1) if c.id == chapter.id)
    for root in ([folder] if folder else []) + [lab.starter_dir]:
        hit = _find(root, chapter, number)
        if hit:
            return hit
    roots = ([folder] if folder else []) + [lab.starter_dir]
    if any((r / "README.md").is_file() for r in roots):
        return "README.md", 1
    for root in roots:
        hit = _find(root, chapter, number, any_todo=True)
        if hit:
            return hit
    return None


def task_focus(lab: LabConfig, chapter: Chapter, task_id: str, folder: Path | None) -> tuple[str, int] | None:
    """The TODO for one task (a task step opens its own file, not the chapter's first one)."""
    number = next(i for i, c in enumerate(lab.chapters, 1) if c.id == chapter.id)
    for root in ([folder] if folder else []) + [lab.starter_dir]:
        hit = _find(root, chapter, number, task_ids=[task_id])
        if hit:
            return hit
    return None


def step_file(lab: LabConfig, path: str, folder: Path | None) -> bool:
    """The step's file exists in the learner's workspace or in the starter (and stays inside them)."""
    for root in ([folder] if folder else []) + [lab.starter_dir]:
        p = (root / path).resolve()
        if p.is_relative_to(root.resolve()) and p.is_file():
            return True
    return False
