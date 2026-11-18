from pathlib import Path

import pytest
from fastapi import HTTPException

from app import workspace_files as wf


@pytest.fixture
def root(tmp_path: Path) -> Path:
    ws = tmp_path / "ws"
    (ws / "pkg" / "sub").mkdir(parents=True)
    (ws / "pkg" / "sub" / "mod.py").write_text("x = 1\n")
    (ws / "greet.py").write_text("print('hi')\n")
    (tmp_path / "secret.txt").write_text("top secret")
    return ws


def assert_403(fn, *args):
    with pytest.raises(HTTPException) as e:
        fn(*args)
    assert e.value.status_code == 403


@pytest.mark.parametrize("rel", ["../x", "a/../../x", "/etc/passwd", "../ws2/x", "pkg/../../secret.txt"])
def test_safe_path_rejects_escapes(root: Path, rel: str):
    assert_403(wf.safe_path, root, rel)


def test_symlink_to_etc_is_blocked(root: Path):
    (root / "etc_link").symlink_to("/etc")
    assert_403(wf.safe_path, root, "etc_link/passwd")
    assert_403(wf.read_file, root, "etc_link/passwd", 1_000_000)
    assert_403(wf.write_file, root, "etc_link/evil", "x", 1_000_000)


def test_symlink_file_outside_is_blocked(root: Path):
    (root / "s").symlink_to(root.parent / "secret.txt")
    assert_403(wf.read_file, root, "s", 1_000_000)
    assert_403(wf.write_file, root, "s", "pwned", 1_000_000)
    assert (root.parent / "secret.txt").read_text() == "top secret"


def test_delete_symlink_removes_link_not_target(root: Path):
    (root / "etc_link").symlink_to(root.parent)
    wf.delete(root, "etc_link")
    assert not (root / "etc_link").is_symlink()
    assert (root.parent / "secret.txt").exists()


def test_normal_nested_paths(root: Path):
    assert wf.safe_path(root, "pkg/sub/mod.py") == (root / "pkg/sub/mod.py").resolve()
    assert wf.read_file(root, "pkg/sub/mod.py", 1_000_000) == "x = 1\n"
    assert wf.safe_path(root, "pkg/./sub/../sub/mod.py") == (root / "pkg/sub/mod.py").resolve()


def test_root_itself(root: Path):
    assert wf.safe_path(root, "") == root.resolve()
    assert wf.safe_path(root, ".") == root.resolve()
    with pytest.raises(HTTPException) as e:
        wf.delete(root, ".")
    assert e.value.status_code == 400
    with pytest.raises(HTTPException) as e:
        wf.write_file(root, "", "x", 100)
    assert e.value.status_code == 400


def test_entry_ops_reject_escapes(root: Path):
    assert_403(wf.delete, root, "../secret.txt")
    assert_403(wf.create, root, "../new.txt", "file")
    assert_403(wf.rename, root, "greet.py", "../moved.py")
    assert_403(wf.rename, root, "/etc/hosts", "h")


def test_null_byte(root: Path):
    with pytest.raises(HTTPException) as e:
        wf.safe_path(root, "greet.py\x00.txt")
    assert e.value.status_code == 400


def test_size_and_binary_limits(root: Path):
    with pytest.raises(HTTPException) as e:
        wf.write_file(root, "big.txt", "x" * 101, 100)
    assert e.value.status_code == 413
    (root / "bin.dat").write_bytes(b"\xff\xfe\x00\x81")
    with pytest.raises(HTTPException) as e:
        wf.read_file(root, "bin.dat", 100)
    assert e.value.status_code == 415


def test_tree_skips_ignored(root: Path):
    (root / "__pycache__").mkdir()
    (root / "__pycache__" / "x.pyc").write_bytes(b"0")
    (root / "Greeter.class").write_bytes(b"0")
    (root / ".git").mkdir()
    (root / "etc_link").symlink_to("/etc")
    names = [n.name for n in wf.list_tree(root)]
    assert names == ["pkg", "greet.py"]


def test_crud(root: Path):
    wf.create(root, "new_dir", "dir")
    wf.create(root, "new_dir/a.py", "file")
    assert wf.write_file(root, "new_dir/a.py", "print(1)\n", 100) == 9
    wf.rename(root, "new_dir/a.py", "new_dir/b.py")
    assert wf.read_file(root, "new_dir/b.py", 100) == "print(1)\n"
    with pytest.raises(HTTPException) as e:
        wf.create(root, "new_dir/b.py", "file")
    assert e.value.status_code == 409
    wf.delete(root, "new_dir")
    assert not (root / "new_dir").exists()
