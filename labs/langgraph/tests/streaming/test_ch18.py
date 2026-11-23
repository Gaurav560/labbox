import r
from fake_openai import Reply


def test_progress_events(fake):
    def check():
        from stream import build_graph
        fake.script = lambda b: Reply("ok")
        got = [chunk["progress"] for chunk in build_graph().stream({"phone": "98220"}, stream_mode="custom")]
        want = ["finding your tickets", "found 2, checking the crew schedule"]
        if got != want:
            return r.failed("progress_events", "In lookup, write = get_stream_writer(), and write({\"progress\": ...}) before and "
                            "after the tickets are found.", want, got)
        r.passed("progress_events", "The slow lookup now tells the screen what it is doing.")
    r.task("progress_events", check)


def test_stream_tokens(fake):
    def check():
        from stream import build_graph, events
        fake.script = lambda b: Reply("T-4471: the East zone crew visits on Wednesday.")
        got = list(events(build_graph(), "98220"))
        tokens = [text for kind, text in got if kind == "token"]
        progress = [text for kind, text in got if kind == "progress"]
        if "".join(tokens) != "T-4471: the East zone crew visits on Wednesday." or len(tokens) < 3:
            return r.failed("stream_tokens", "Yield the reply node's message chunks one by one from stream_mode=[\"custom\", "
                            "\"messages\"], not the finished reply.", "many small tokens", f"{len(tokens)} piece(s)")
        if len(progress) != 2 or got[0][0] != "progress":
            return r.failed("stream_tokens", "Yield the custom progress events too, as (\"progress\", text), in order.")
        r.passed("stream_tokens", "Progress first, then the reply word by word: nobody stares at an empty screen.")
    r.task("stream_tokens", check)
