import os
import uuid

import r


def _fresh(fails):
    import board
    os.environ["SMS_FAILS"] = str(fails)
    board.ATTEMPTS["sms"] = 0
    if board.RECORD.exists():
        board.RECORD.unlink()
    return board


def test_task_steps():
    def check():
        from flow import repair_job
        board = _fresh(1)
        job = f"J-{uuid.uuid4().hex[:6]}"
        config = {"configurable": {"thread_id": job}}
        try:
            repair_job.invoke({"job": job, "estimate": 18000}, config)
        except Exception:  # noqa: BLE001
            pass
        result = repair_job.invoke(None, config)
        lines = board.RECORD.read_text().splitlines()
        if sum("parts ordered" in line for line in lines) != 1 or sum("crew booked" in line for line in lines) != 1:
            return r.failed("task_steps", "After the SMS crash, resuming booked the crew or ordered the parts again. Put @task on "
                            "book_crew, order_parts and send_sms, and call each with .result().",
                            "1 crew, 1 parts order", f"{sum('crew booked' in l for l in lines)} crew, "
                            f"{sum('parts ordered' in l for l in lines)} parts orders")
        if not result or "SMS sent" not in result[-1]:
            return r.failed("task_steps", "The resumed job should finish with the SMS.", "SMS sent", result)
        r.passed("task_steps", "Finished tasks were read from the checkpoint; only the SMS ran again.")
    r.task("task_steps", check)


def test_approval_in_flow():
    def check():
        from langgraph.types import Command
        from flow import repair_job
        _fresh(0)
        job = f"J-{uuid.uuid4().hex[:6]}"
        config = {"configurable": {"thread_id": job}}
        repair_job.invoke({"job": job, "estimate": 65000}, config)
        asked = repair_job.get_state(config).interrupts
        if not asked or asked[0].value.get("estimate") != 65000:
            return r.failed("approval_in_flow", "A Rs 65,000 job must stop for approval: interrupt({...}) when the estimate is over "
                            "APPROVAL_OVER.", "a pause with the estimate", "no pause")
        result = repair_job.invoke(Command(resume={"approve": False, "note": "no budget"}), config)
        if result != [f"{job}: refused (no budget)"]:
            return r.failed("approval_in_flow", "When the answer's approve is false, return [f\"{job}: refused ({note})\"].",
                            [f"{job}: refused (no budget)"], result)
        r.passed("approval_in_flow", "interrupt works inside plain Python too: the job paused, and the refusal ended it.")
    r.task("approval_in_flow", check)
