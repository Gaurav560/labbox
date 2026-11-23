import os

import r


def _fresh(fails):
    import board
    os.environ["SMS_FAILS"] = str(fails)
    board.ATTEMPTS["sms"] = 0
    if board.RECORD.exists():
        board.RECORD.unlink()
    return board


def test_retry_sms():
    def check():
        from langgraph.checkpoint.memory import InMemorySaver
        from job import build_graph
        board = _fresh(2)
        app = build_graph(InMemorySaver())
        try:
            state = app.invoke({"job": "J-1"}, {"configurable": {"thread_id": "J-1"}})
        except Exception as e:  # noqa: BLE001
            return r.failed("retry_sms", "The SMS gateway timed out twice and the run failed: give notify_citizen "
                            "retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.5, retry_on=SmsTimeout).",
                            "3 attempts, then success", f"{board.ATTEMPTS['sms']} attempt(s), then {type(e).__name__}")
        if board.ATTEMPTS["sms"] != 3 or "J-1: SMS sent to the citizen" not in state["log"]:
            return r.failed("retry_sms", "Expected two timeouts and a third attempt that works.", 3, board.ATTEMPTS["sms"])
        r.passed("retry_sms", "Two timeouts, then the SMS went: the retry policy handled a flaky service.")
    r.task("retry_sms", check)


def test_resume_job():
    def check():
        from langgraph.checkpoint.memory import InMemorySaver
        from job import build_graph, run_job
        board = _fresh(99)
        app = build_graph(InMemorySaver())
        try:
            run_job(app, "J-2")
            return r.failed("resume_job", "The SMS gateway was down, so the first run should have failed (finish retry_sms too).")
        except Exception:  # noqa: BLE001
            pass
        board.ATTEMPTS["sms"] = 0
        os.environ["SMS_FAILS"] = "0"
        state = run_job(app, "J-2")
        orders = [line for line in board.RECORD.read_text().splitlines() if "parts ordered" in line]
        if len(orders) != 1:
            return r.failed("resume_job", "After the crash, run_job started the job again and ordered the parts twice. When "
                            "app.get_state(config).next is not empty, continue with app.invoke(None, config).",
                            "1 parts order", f"{len(orders)} parts orders")
        if "J-2: SMS sent to the citizen" not in state["log"]:
            return r.failed("resume_job", "The resumed run should finish with the SMS.")
        r.passed("resume_job", "The job continued at the SMS: the crew and the parts were not booked twice.")
    r.task("resume_job", check)
