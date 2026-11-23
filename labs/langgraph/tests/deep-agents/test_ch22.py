import os
import shutil
import tempfile

import r
from fake_openai import Reply


def data_copy() -> str:
    root = tempfile.mkdtemp()
    for name in os.listdir("data"):
        shutil.copy(os.path.join("data", name), root)
    return root


def is_analyst(body, fake) -> bool:
    return "count_complaints" in fake.tool_names(body)


def test_deep_agent(fake):
    def check():
        from planner import build_agent

        def script(body):
            if any(m.get("role") == "tool" for m in body["messages"]):
                return Reply("The plan is in /plan.md.")
            return Reply.tool("write_file", {"file_path": "/plan.md", "content": "1. Station Road: replace the main."})
        fake.script = script
        root = data_copy()
        build_agent(root).invoke({"messages": [("user", "Prepare the plan.")]})
        task = [t["function"]["description"] for t in fake.chat_requests[0].get("tools", []) if t["function"]["name"] == "task"]
        if not task or "data-analyst" not in task[0]:
            return r.failed("deep_agent", "The planner cannot hand work to the data-analyst: pass subagents=[ANALYST].",
                            "a task tool that lists data-analyst", "no data-analyst")
        plan = os.path.join(root, "plan.md")
        if not os.path.exists(plan):
            return r.failed("deep_agent", "write_file did not reach the data folder: pass backend=FilesystemBackend(root_dir=root, "
                            "virtual_mode=True).", "data/plan.md written", "no file on disk")
        r.passed("deep_agent", "The planner can delegate to the data-analyst, and its files are the real files in data/.")
    r.task("deep_agent", check)


def test_analyst_subagent(fake):
    def check():
        from planner import build_agent
        seen = {}

        def script(body):
            tools_done = [m for m in body["messages"] if m.get("role") == "tool"]
            if is_analyst(body, fake):
                if tools_done:
                    seen["result"] = tools_done[-1].get("content")
                    return Reply("Station Road had 41 leak complaints.")
                return Reply.tool("count_complaints", {"street": "Station Road", "kind": "leak"})
            if tools_done:
                return Reply("Done.")
            return Reply.tool("task", {"description": "How many leak complaints did Station Road have?",
                                       "subagent_type": "data-analyst"})
        fake.script = script
        build_agent(data_copy()).invoke({"messages": [("user", "Prepare the plan.")]})
        if "result" not in seen:
            return r.failed("analyst_subagent", "The data-analyst has no count_complaints tool: add \"tools\": [count_complaints] to "
                            "ANALYST (and finish deep_agent so the planner can reach it).")
        if "Station Road, leak: 41" not in str(seen["result"]):
            return r.failed("analyst_subagent", "count_complaints ran, but returned something unexpected.", "Station Road, leak: 41",
                            seen["result"])
        r.passed("analyst_subagent", "The planner asked, the analyst counted with Python: 41 Station Road leaks, exactly.")
    r.task("analyst_subagent", check)
