import r
from fake_openai import Reply


def test_first_agent(fake):
    def check():
        from agent import SYSTEM, navin_agent
        agent = navin_agent()
        if agent is None:
            return r.failed("first_agent", "navin_agent() returned None. Return create_agent(\"openai:ai-chat\", tools=[...], system_prompt=SYSTEM).")
        fake.script = lambda b: Reply.tool("storage_cost", {"crates": 25, "days": 7}) if len(fake.chat_requests) == 1 else Reply("Rs 350.")
        result = agent.invoke({"messages": [{"role": "user", "content": "25 crates for a week?"}]})
        first = fake.chat_requests[0]
        if sorted(fake.tool_names(first)) != ["mandi_price", "storage_cost"]:
            return r.failed("first_agent", "Give the agent both tools: tools=[mandi_price, storage_cost].", "['mandi_price', 'storage_cost']", fake.tool_names(first))
        if fake.texts(first, "system") != [SYSTEM]:
            return r.failed("first_agent", "Pass system_prompt=SYSTEM, so Navin knows who it is and to use its tools.")
        if len(fake.chat_requests) < 2 or result["messages"][-1].content != "Rs 350.":
            return r.failed("first_agent", "The agent should run the tool and call the model again with the result.")
        r.passed("first_agent", "Chapter 10's loop, in one line: create_agent runs the model, the tools and the loop for you.")
    r.task("first_agent", check)


def test_tools_used():
    def check():
        from agent import tools_used
        from langchain.messages import AIMessage, HumanMessage, ToolMessage
        result = {"messages": [HumanMessage("q"),
                               AIMessage("", tool_calls=[{"name": "mandi_price", "args": {"crop": "onion"}, "id": "1"},
                                                         {"name": "storage_cost", "args": {"crates": 1, "days": 1}, "id": "2"}]),
                               ToolMessage("1850", tool_call_id="1"), ToolMessage("2", tool_call_id="2"),
                               AIMessage("", tool_calls=[{"name": "mandi_price", "args": {"crop": "tomato"}, "id": "3"}]),
                               ToolMessage("1200", tool_call_id="3"), AIMessage("done")]}
        got = tools_used(result)
        want = ["mandi_price", "storage_cost", "mandi_price"]
        if got != want:
            return r.failed("tools_used", "Collect the name of every tool call of every AI message, in order (a message can hold several calls).", want, got)
        r.passed("tools_used", "The messages list is the whole story of a run: who asked what, and what came back.")
    r.task("tools_used", check)
