"""Phase H2: state the workers share (app/shared.py). Runs in memory by default and in Redis with
LABBOX_TEST_REDIS_URL; the cross-process test needs Redis, because that is the point of it."""
import asyncio
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
from fastapi import HTTPException

from app import checker, shared

BACKEND = Path(__file__).resolve().parents[1]


def test_a_lock_has_one_holder_at_a_time():
    inside, most = 0, 0
    guard = threading.Lock()

    def work():
        nonlocal inside, most
        with shared.lock("test:machine"):
            with guard:
                inside += 1
                most = max(most, inside)
            time.sleep(0.05)
            with guard:
                inside -= 1

    threads = [threading.Thread(target=work) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert most == 1


def test_a_claim_is_taken_once_and_frees_itself():
    token = shared.claim("test:slot", 0.3)
    assert token
    assert shared.claim("test:slot", 0.3) is None
    shared.release("test:slot", "not-the-owner")  # someone else's token frees nothing
    assert shared.claim("test:slot", 0.3) is None
    time.sleep(0.4)  # a crashed holder never keeps it forever
    again = shared.claim("test:slot", 5)
    assert again
    shared.release("test:slot", again)
    assert shared.claim("test:slot", 5)


def test_a_lease_stays_with_its_holder_until_it_lapses():
    assert shared.keep("test:leader", "worker-a", 0.3)
    assert shared.keep("test:leader", "worker-a", 0.3)  # renewing
    assert not shared.keep("test:leader", "worker-b", 0.3)
    time.sleep(0.4)  # worker-a died: worker-b takes over
    assert shared.keep("test:leader", "worker-b", 0.3)


def test_counters_count_the_last_window_only():
    shared.forget_hits()
    for _ in range(3):
        shared.hit("test:ai", 0.3)
    assert shared.recent("test:ai", 0.3) == 3
    time.sleep(0.4)
    assert shared.recent("test:ai", 0.3) == 0


def test_one_check_per_learner():
    async def go():
        async with checker.check_slot(4242):
            with pytest.raises(HTTPException) as e:
                async with checker.check_slot(4242):
                    pass
            assert e.value.status_code == 429
            async with checker.check_slot(4243):  # another learner is not blocked
                pass
        async with checker.check_slot(4242):  # free again afterwards
            pass

    asyncio.run(go())


@pytest.mark.skipif(not os.environ.get("LABBOX_TEST_REDIS_URL"), reason="needs Redis (LABBOX_TEST_REDIS_URL)")
def test_workers_in_other_processes_see_the_same_state():
    """Another process (as another uvicorn worker would) holds a learner's check slot and a machine lock."""
    holder = subprocess.Popen(
        [sys.executable, "-c", (
            "import sys, time; from app import shared\n"
            "assert shared.claim('check:777', 30)\n"
            "with shared.lock('lab-u777-go-basics'):\n"
            "    print('holding', flush=True); time.sleep(1.5)\n"
        )],
        cwd=BACKEND, env={**os.environ, "REDIS_URL": os.environ["LABBOX_TEST_REDIS_URL"]},
        stdout=subprocess.PIPE, text=True,
    )
    try:
        assert holder.stdout.readline().strip() == "holding"
        assert shared.claim("check:777", 30) is None  # the other worker's check is running
        with pytest.raises(shared.Busy):
            with shared.lock("lab-u777-go-basics", wait=0.3):
                pass
        started = time.monotonic()
        with shared.lock("lab-u777-go-basics", wait=10):  # waits for its turn, then gets it
            assert time.monotonic() - started > 0.3
    finally:
        holder.wait(timeout=10)
