import r
from fake_openai import Reply


def test_agent_node(fake):
    def check():
        from langchain.messages import HumanMessage
        from agent import agent
        fake.script = lambda b: Reply("Please tell me your phone number.")
        agent({"messages": [HumanMessage("Any update?")]})
        names = fake.tool_names(fake.chat_requests[-1])
        if sorted(names) != ["find_tickets", "ticket_status"]:
            return r.failed("agent_node", "The model was not given the tools: use model().bind_tools(TOOLS).invoke(...).",
                            ["find_tickets", "ticket_status"], names)
        r.passed("agent_node", "The model now sees both ticket tools and can ask for them.")
    r.task("agent_node", check)


def test_tool_loop(fake):
    def check():
        from langchain.messages import AIMessage
        from langgraph.graph import END
        from agent import build_graph, should_continue
        asking = AIMessage("", tool_calls=[{"name": "find_tickets", "args": {"phone": "98220"}, "id": "c1"}])
        if should_continue({"messages": [asking]}) != "tools" or should_continue({"messages": [AIMessage("Done.")]}) != END:
            return r.failed("tool_loop", "Return \"tools\" when the last message has tool_calls, and END when it does not.")

        def script(body):
            if any(m.get("role") == "tool" for m in body["messages"]):
                return Reply("You have two open tickets.")
            return Reply.tool("find_tickets", {"phone": "98220"})
        fake.script = script
        state = build_graph().invoke({"messages": [("user", "98220")]}, {"configurable": {"thread_id": "t"}})
        tool_results = [m.content for m in state["messages"] if m.type == "tool"]
        if not tool_results or "T-4471" not in tool_results[0] or state["messages"][-1].content != "You have two open tickets.":
            return r.failed("tool_loop", "The tool should run and its result go back to the model, which then answers.")
        r.passed("tool_loop", "Model, tools, model: the agent loop is two nodes and a conditional edge.")
    r.task("tool_loop", check)
