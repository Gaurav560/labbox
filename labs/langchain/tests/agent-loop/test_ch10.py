import r
from fake_openai import Reply


def test_run_tool_call():
    def check():
        from coop_tools import mandi_price, storage_cost
        from loop import run_tool_call
        tools = {"mandi_price": mandi_price, "storage_cost": storage_cost}
        m = run_tool_call({"name": "storage_cost", "args": {"crates": 60, "days": 10}, "id": "call_7"}, tools)
        if m.content != "1200":
            return r.failed("run_tool_call", "Run the tool the model named, with its args, and put str(result) in the ToolMessage.", "1200", m.content)
        if m.tool_call_id != "call_7":
            return r.failed("run_tool_call", "Keep the call's id in tool_call_id: it tells the model which request this result answers.", "call_7", m.tool_call_id)
        bad = run_tool_call({"name": "mandi_price", "args": {"crop": "garlic"}, "id": "call_8"}, tools)
        if not bad.content.startswith("Error:") or "garlic" not in bad.content:
            return r.failed("run_tool_call", "When a tool raises an exception, return a ToolMessage with \"Error: \" and the exception's text, so the model can read it.",
                            "Error: The co-op has no rate for garlic...", bad.content)
        r.passed("run_tool_call", "The model only asked; your code ran Python and handed back the result, or the error, with the call's id.")
    r.task("run_tool_call", check)


def test_agent_loop(fake):
    def check():
        from langchain.chat_models import init_chat_model
        from langchain.messages import HumanMessage

        from coop_tools import mandi_price, storage_cost
        from loop import agent_loop

        def script(body):
            n = len(fake.chat_requests)
            if n == 1:
                return Reply.tool("mandi_price", {"crop": "onion"}, ("storage_cost", {"crates": 60, "days": 10}))
            return Reply("Onion is Rs 1,850 a quintal; storing 60 crates for 10 days costs Rs 1,200.")
        fake.script = script
        messages = [HumanMessage("rate and storage?")]
        answer = agent_loop(init_chat_model("openai:ai-chat"), messages, [mandi_price, storage_cost])
        if len(fake.chat_requests) < 2:
            return r.failed("agent_loop", "The model asked for two tools, but was never called again with their results. Loop: call the model, run "
                            "the tool calls, add the results, and call it again until it answers.", "2 model calls", len(fake.chat_requests))
        second = fake.chat_requests[1]["messages"]
        tool_results = [m["content"] for m in second if m["role"] == "tool"]
        if sorted(tool_results) != ["1200", "1850"]:
            return r.failed("agent_loop", "The second request should carry both tool results (add a ToolMessage for every call in reply.tool_calls).",
                            "['1200', '1850']", tool_results)
        if getattr(answer, "content", None) != "Onion is Rs 1,850 a quintal; storing 60 crates for 10 days costs Rs 1,200.":
            return r.failed("agent_loop", "Return the reply that has no tool calls: the final answer.")
        fake.reset()
        fake.script = lambda b: Reply.tool("mandi_price", {"crop": "onion"})
        try:
            agent_loop(init_chat_model("openai:ai-chat"), [HumanMessage("loop forever")], [mandi_price], max_steps=3)
            return r.failed("agent_loop", "A model that keeps asking for tools must not loop forever: after max_steps, raise RuntimeError.")
        except RuntimeError:
            pass
        if len(fake.chat_requests) != 3:
            return r.failed("agent_loop", "Call the model at most max_steps times.", 3, len(fake.chat_requests))
        r.passed("agent_loop", "That loop is an agent: the model decides, your code acts, and max_steps keeps the bill bounded.")
    r.task("agent_loop", check)
