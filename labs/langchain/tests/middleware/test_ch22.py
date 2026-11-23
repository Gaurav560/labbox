import r
from fake_openai import Reply


class Req:
    tool_call = {"name": "mandi_price", "args": {"crop": "garlic"}, "id": "1"}


def test_tool_errors(fake):
    def check():
        from agent import on_tool_error
        got = on_tool_error(ValueError("The co-op has no rate for garlic"), Req())
        if got != "mandi_price failed: The co-op has no rate for garlic":
            return r.failed("tool_errors", "For a ValueError return f\"{request.tool_call['name']} failed: {error}\".",
                            "mandi_price failed: The co-op has no rate for garlic", got)
        if on_tool_error(KeyError("database password wrong"), Req()) is not None:
            return r.failed("tool_errors", "Any other exception should return None: internal errors must not reach the model or the member.")
        r.passed("tool_errors", "A member's mistake becomes a message the model can explain; an internal error stops the run and stays private.")
    r.task("tool_errors", check)


def test_limits_and_summaries(fake):
    def check():
        from agent import navin_agent
        agent = navin_agent()
        fake.script = lambda b: Reply.tool("mandi_price", {"crop": "garlic"}) if len(fake.chat_requests) == 1 else Reply("We do not trade garlic.")
        try:
            result = agent.invoke({"messages": [{"role": "user", "content": "garlic rate?"}]}, {"configurable": {"thread_id": "a"}})
        except ValueError:
            return r.failed("limits_and_summaries", "The tool's error stopped the run: add ToolErrorMiddleware(on_tool_error) to middleware.")
        tools = [m["content"] for m in fake.chat_requests[-1]["messages"] if m["role"] == "tool"]
        if not tools or "garlic" not in str(tools[0]):
            return r.failed("limits_and_summaries", "The error message should reach the model as the tool's result (ToolErrorMiddleware).")
        fake.reset()
        fake.script = lambda b: Reply.tool("storage_cost", {"crates": 1, "days": 1})
        agent.invoke({"messages": [{"role": "user", "content": "loop"}]}, {"configurable": {"thread_id": "b"}})
        agent_calls = [b for b in fake.chat_requests if b.get("tools")]  # summaries are model calls too, without tools
        if len(agent_calls) != 5:
            return r.failed("limits_and_summaries", "A model that keeps calling tools should be stopped after 5 calls: ModelCallLimitMiddleware(run_limit=5, exit_behavior=\"end\").",
                            5, len(agent_calls))
        fake.reset()
        fake.script = lambda b: Reply("A short summary." if "summar" in str(b).lower() else "ok")
        config = {"configurable": {"thread_id": "c"}}
        for i in range(6):
            agent.invoke({"messages": [{"role": "user", "content": f"message number {i}"}]}, config)
        kept = agent.get_state(config).values["messages"]
        if len(kept) >= 12:
            return r.failed("limits_and_summaries", "Long conversations should be summarised: SummarizationMiddleware(\"openai:ai-chat\", trigger=(\"messages\", 8), keep=(\"messages\", 4)).",
                            "fewer than 12 messages kept", len(kept))
        r.passed("limits_and_summaries", f"Errors explained, runaways stopped at 5 calls, and 12 messages kept as {len(kept)}: three lines of middleware.")
    r.task("limits_and_summaries", check)
