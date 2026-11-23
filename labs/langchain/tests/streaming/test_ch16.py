import r
from fake_openai import Reply


def script_for(fake):
    def script(body):
        if len(fake.chat_requests) == 1:
            return Reply.tool("storage_cost", {"crates": 30, "days": 6})
        return Reply("Storing 30 crates for 6 days costs Rs 360.")
    return script


def test_stream_steps(fake):
    def check():
        from streaming import navin_agent, steps
        fake.script = script_for(fake)
        seen = []
        got = steps(navin_agent(), "30 crates, 6 days?", seen.append)
        want = ["model: asks for storage_cost", "tools: ToolMessage", "model: AIMessage"]
        if got != want:
            return r.failed("stream_steps", "One line per new message of each update: \"step: asks for name\" for tool calls, else \"step: MessageType\".", want, got)
        if seen != want:
            return r.failed("stream_steps", "Also call on_line(line) for each line as you add it, so a display can show it at once.", want, seen)
        r.passed("stream_steps", "Each step reported the moment it finished: the model asked, the tool ran, the model answered.")
    r.task("stream_steps", check)


def test_stream_answer_text(fake):
    def check():
        from streaming import answer_text, navin_agent
        fake.script = script_for(fake)
        pieces = []
        got = answer_text(navin_agent(), "30 crates, 6 days?", pieces.append)
        if got != "Storing 30 crates for 6 days costs Rs 360.":
            return r.failed("stream_answer_text", "Join the text pieces from the model step; skip tool results and empty chunks.",
                            "Storing 30 crates for 6 days costs Rs 360.", got)
        if len(pieces) < 4 or "" in pieces or "360" in "".join(pieces[:1]):
            return r.failed("stream_answer_text", "Call on_piece for every non-empty piece as it arrives, not once at the end.")
        r.passed("stream_answer_text", "The answer streamed word by word, while the tool step and its result stayed out of the text.")
    r.task("stream_answer_text", check)
