import os
import tempfile

import r
from fake_openai import Reply


def _counting(fake):
    fake.script = lambda b: Reply(f"seen {len(fake.texts(b, 'user'))}")


def test_thread_memory(fake):
    def check():
        from langgraph.checkpoint.memory import InMemorySaver
        from chat import ask, build_graph
        _counting(fake)
        app = build_graph(InMemorySaver())
        ask(app, "98220", "No water in Tilak Nagar")
        second = ask(app, "98220", "Any update?")
        if second != "seen 2":
            return r.failed("thread_memory", "The second message from the same phone should reach the model with the first: "
                            "compile(checkpointer=checkpointer), and invoke with {\"configurable\": {\"thread_id\": phone}}.",
                            "2 citizen messages sent to the model", second.replace("seen ", "") + " citizen message(s)")
        other = ask(app, "70300", "Any update?")
        if other != "seen 1":
            return r.failed("thread_memory", "Another phone number must start its own thread: use the phone as the thread_id.",
                            "1 citizen message", other.replace("seen ", "") + " citizen message(s)")
        r.passed("thread_memory", "One thread per phone: the checkpointer saved each conversation, and only its own.")
    r.task("thread_memory", check)


def test_sqlite_saver(fake):
    def check():
        from langgraph.checkpoint.sqlite import SqliteSaver
        from chat import ask, build_graph, open_saver
        _counting(fake)
        path = os.path.join(tempfile.mkdtemp(), "harsh.db")
        saver = open_saver(path)
        if not isinstance(saver, SqliteSaver):
            return r.failed("sqlite_saver", "open_saver should return SqliteSaver(sqlite3.connect(path, check_same_thread=False)).",
                            "a SqliteSaver", type(saver).__name__)
        ask(build_graph(saver), "98220", "No water in Tilak Nagar")
        again = ask(build_graph(open_saver(path)), "98220", "Any update?")
        if again != "seen 2":
            return r.failed("sqlite_saver", "A new saver on the same file should find the earlier message (finish task "
                            "thread_memory first if it is not done).", "2 citizen messages", again.replace("seen ", ""))
        r.passed("sqlite_saver", "The chat survived a restart: a new app on the same file found the thread.")
    r.task("sqlite_saver", check)
