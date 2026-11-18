"""Safe file operations inside a user's workspace folder on the host.

Every path from the browser is relative to the workspace root and goes through
safe_path() (or safe_entry() for operations on the entry itself, like delete).
"""
import fnmatch
import os
import shutil
import sys
from pathlib import Path
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel

LEARNER_UID = 1000
LEARNER_GID = 1000
IGNORED_NAMES = {"__pycache__", ".git", "node_modules", ".venv"}
IGNORED_PATTERNS = ("*.class",)
TREE_MAX_FILE_BYTES = 1_000_000
TREE_MAX_ENTRIES = 2000
TREE_MAX_DEPTH = 12


class FileNode(BaseModel):
    path: str
    name: str
    type: Literal["file", "dir"]
    children: list["FileNode"] | None = None


def is_ignored(name: str) -> bool:
    return name in IGNORED_NAMES or any(fnmatch.fnmatch(name, p) for p in IGNORED_PATTERNS)


def safe_path(root: Path, rel: str) -> Path:
    if "\x00" in rel:
        raise HTTPException(400, "Invalid path")
    root = root.resolve()
    target = (root / rel).resolve()
    if target != root and root not in target.parents:
        raise HTTPException(403, "Path outside workspace")
    return target


def safe_entry(root: Path, rel: str) -> Path:
    """Path to the entry itself (symlinks NOT followed for the last part).

    Used for delete and rename so that removing a symlink removes the link,
    not whatever it points to. The parent folder must resolve inside root.
    """
    root = root.resolve()
    if "\x00" in rel:
        raise HTTPException(400, "Invalid path")
    parts = Path(rel).parts  # an absolute rel keeps "/" as its first part and fails below
    if not parts or parts[-1] in ("", ".", ".."):
        raise HTTPException(400, "Invalid path")
    parent = safe_path(root, str(Path(*parts[:-1])) if len(parts) > 1 else "")
    entry = parent / parts[-1]
    if entry == root:
        raise HTTPException(400, "Cannot change the workspace root")
    return entry


def chown(path: Path) -> None:
    if sys.platform != "linux":
        return
    try:
        os.chown(path, LEARNER_UID, LEARNER_GID, follow_symlinks=False)
    except PermissionError:
        pass  # backend not root and file already ours: fine


def chown_tree(root: Path) -> None:
    if sys.platform != "linux":
        return
    chown(root)
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for name in dirnames + filenames:
            chown(Path(dirpath) / name)


def _rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix()


def list_tree(root: Path) -> list[FileNode]:
    root = root.resolve()
    count = 0

    def walk(folder: Path, depth: int) -> list[FileNode]:
        nonlocal count
        nodes: list[FileNode] = []
        try:
            entries = sorted(os.scandir(folder), key=lambda e: (not e.is_dir(follow_symlinks=False), e.name.lower()))
        except OSError:
            return nodes
        for e in entries:
            if count >= TREE_MAX_ENTRIES or is_ignored(e.name):
                continue
            p = Path(e.path)
            if e.is_symlink():
                # Show symlinks to files inside the workspace; never follow symlinked dirs.
                try:
                    target = p.resolve()
                except OSError:
                    continue
                if root not in target.parents or not target.is_file():
                    continue
                if target.stat().st_size > TREE_MAX_FILE_BYTES:
                    continue
                nodes.append(FileNode(path=_rel(root, p), name=e.name, type="file"))
            elif e.is_dir(follow_symlinks=False):
                children = walk(p, depth + 1) if depth < TREE_MAX_DEPTH else []
                nodes.append(FileNode(path=_rel(root, p), name=e.name, type="dir", children=children))
            elif e.is_file(follow_symlinks=False):
                if e.stat(follow_symlinks=False).st_size > TREE_MAX_FILE_BYTES:
                    continue
                nodes.append(FileNode(path=_rel(root, p), name=e.name, type="file"))
            else:
                continue
            count += 1
        return nodes

    return walk(root, 0)


def read_file(root: Path, rel: str, max_bytes: int) -> str:
    target = safe_path(root, rel)
    if not target.is_file():
        raise HTTPException(404, "File not found")
    if target.stat().st_size > max_bytes:
        raise HTTPException(413, f"File is larger than {max_bytes} bytes")
    try:
        return target.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(415, "Binary file, cannot open in editor")


def write_file(root: Path, rel: str, content: str, max_bytes: int) -> int:
    target = safe_path(root, rel)
    if target == root.resolve() or target.is_dir():
        raise HTTPException(400, "Path is a folder")
    data = content.encode("utf-8")
    if len(data) > max_bytes:
        raise HTTPException(413, f"File is larger than {max_bytes} bytes")
    if not target.parent.is_dir():
        raise HTTPException(404, "Parent folder does not exist")
    target.write_bytes(data)
    chown(target)
    return len(data)


def create(root: Path, rel: str, kind: Literal["file", "dir"]) -> None:
    target = safe_entry(root, rel)
    if target.exists() or target.is_symlink():
        raise HTTPException(409, "Already exists")
    if not target.parent.is_dir():
        raise HTTPException(404, "Parent folder does not exist")
    if kind == "dir":
        target.mkdir()
    else:
        target.touch()
    chown(target)


def rename(root: Path, src: str, dst: str) -> None:
    s = safe_entry(root, src)
    d = safe_entry(root, dst)
    if not (s.exists() or s.is_symlink()):
        raise HTTPException(404, "Source not found")
    if d.exists() or d.is_symlink():
        raise HTTPException(409, "Destination already exists")
    if not d.parent.is_dir():
        raise HTTPException(404, "Destination folder does not exist")
    if s.is_dir() and not s.is_symlink() and (s == d or s in d.parents):
        raise HTTPException(400, "Cannot move a folder into itself")
    s.rename(d)


def delete(root: Path, rel: str) -> None:
    target = safe_entry(root, rel)
    if target.is_symlink() or target.is_file():
        target.unlink()
    elif target.is_dir():
        shutil.rmtree(target)
    else:
        raise HTTPException(404, "Not found")


def clear_dir(root: Path) -> None:
    """Delete everything inside root (used by reset)."""
    for entry in root.iterdir():
        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
        else:
            entry.unlink()
