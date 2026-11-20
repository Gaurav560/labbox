"""Phase H3: background jobs (app/jobs.py): images, unused lab networks, database backups."""
import os
import random
import sqlite3
import subprocess
from pathlib import Path

import pytest
from sqlalchemy.engine import make_url

from docker.types import IPAMConfig, IPAMPool

from app import containers, jobs, services
from app.config import get_settings
from app.labs import CHECKER_IMAGE, all_labs, init_labs


@pytest.fixture(autouse=True, scope="module")
def labs():
    init_labs(get_settings().LABS_DIR)


def test_docker_timestamps_with_nanoseconds_and_offsets():
    assert jobs._created("2026-11-20T00:45:01.817815011+05:30") == jobs._created("2026-11-19T19:15:01.817815Z")
    assert jobs._created("garbage") > 0  # unreadable: treated as just made, so never removed


def test_wanted_images_cover_labs_services_checker_and_relay():
    wanted = jobs.wanted_images()
    assert {lab.image for lab in all_labs()} <= set(wanted)
    assert wanted[CHECKER_IMAGE] is True  # built here, never pulled
    assert wanted["postgres:16"] is False and wanted["redis:7.4"] is False  # pulled when missing


def test_sqlite_backup_is_a_checked_copy_and_old_ones_rotate(tmp_path, monkeypatch):
    db = tmp_path / "live.db"
    with sqlite3.connect(db) as c:
        c.execute("CREATE TABLE user (id INTEGER PRIMARY KEY, username TEXT)")
        c.execute("INSERT INTO user (username) VALUES ('asha')")
    folder = tmp_path / "backups"
    folder.mkdir()
    for i in range(5):  # older backups, oldest first by name
        (folder / f"labbox-2026010{i}-000000.sqlite").write_bytes(b"old")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    monkeypatch.setenv("BACKUP_DIR", str(folder))
    monkeypatch.setenv("BACKUP_KEEP", "3")
    get_settings.cache_clear()
    try:
        r = jobs.run("backup")
    finally:
        get_settings.cache_clear()
    assert r.ok, r.summary
    kept = sorted(p.name for p in folder.iterdir())
    assert len(kept) == 3 and kept[0] == "labbox-20260103-000000.sqlite"  # the two oldest went
    newest = folder / kept[-1]
    assert oct(newest.stat().st_mode & 0o777) == "0o600"
    with sqlite3.connect(newest) as c:
        assert c.execute("SELECT username FROM user").fetchone() == ("asha",)


@pytest.mark.docker
@pytest.mark.skipif(not os.environ.get("LABBOX_TEST_DATABASE_URL"), reason="needs a Postgres test server")
def test_postgres_backup_restores(tmp_path, monkeypatch):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))
    r = jobs.run("backup")
    assert r.ok, r.summary
    dump = next(tmp_path.glob("labbox-*.dump"))
    listing = subprocess.run(["docker", "run", "--rm", "-i", "postgres:16", "pg_restore", "--list"],
                             stdin=dump.open("rb"), capture_output=True, text=True)
    assert " TABLE DATA public user " in listing.stdout
    assert make_url(get_settings().DATABASE_URL).password not in Path(dump).read_bytes().decode(errors="ignore")


@pytest.mark.docker
def test_images_job_reports_without_pulling():
    ok, summary = jobs.images_job(pull=False)
    assert "images checked" in summary
    assert ok, summary  # every lab image is built on a machine that runs the Docker tests


@pytest.mark.docker
def test_unused_lab_networks_go_and_used_ones_stay():
    c = containers.client()
    user = random.randint(10_000_000, 89_000_000)  # never a real account
    labels = lambda lab: {"labbox": "true", "labbox.kind": "network", "labbox.user": str(user), "labbox.lab": lab}  # noqa: E731
    def make(lab):  # a small subnet from the lab pool, as real lab networks get (Docker's own pool runs out)
        ipam = IPAMConfig(pool_configs=[IPAMPool(subnet=services._free_subnet())])
        return c.networks.create(f"labnet-u{user}-{lab}", labels=labels(lab), ipam=ipam)

    lonely = make("lonely")
    used = make("used")
    stopped = c.containers.create("alpine/socat:1.8.0.3", name=f"lab-u{user}-used",
                                  labels={"labbox": "true", "labbox.kind": "workspace", "labbox.user": str(user), "labbox.lab": "used"})
    try:
        ok, summary = jobs.networks_job(min_age=3600)  # both are brand new: nothing goes
        assert {n.name for n in c.networks.list(names=[f"labnet-u{user}-"])} >= {lonely.name, used.name}
        ok, summary = jobs.networks_job(min_age=0)
        names = {n.name for n in c.networks.list(names=[f"labnet-u{user}-"])}
        assert lonely.name not in names, summary
        assert used.name in names  # a stopped machine keeps its network
    finally:
        stopped.remove(force=True)
        for n in c.networks.list(names=[f"labnet-u{user}-"]):
            n.remove()


def test_the_schedule_is_in_utc(monkeypatch):
    """arq uses the machine's own zone unless told otherwise; the backup hour is a UTC hour."""
    import importlib
    from datetime import timezone

    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:1/0")  # never connected to: only the settings are read
    get_settings.cache_clear()
    try:
        import app.worker

        WorkerSettings = importlib.reload(app.worker).WorkerSettings
    finally:
        get_settings.cache_clear()

    assert WorkerSettings.timezone == timezone.utc
    backup = next(c for c in WorkerSettings.cron_jobs if c.name == "cron:job_backup")
    assert backup.hour == {get_settings().BACKUP_HOUR_UTC}
