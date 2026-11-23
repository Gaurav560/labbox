"""An agent, by hand: the model may ask for tools; we run them and send the results back, until it answers."""
from langchain.messages import AIMessage, ToolMessage


def run_tool_call(call: dict, tools_by_name: dict) -> ToolMessage:
    """Runs one tool call the model asked for, and wraps the result for the model."""
    try:
        result = tools_by_name[call["name"]].invoke(call["args"])
        return ToolMessage(content=str(result), tool_call_id=call["id"])
    except Exception as e:  # the model reads the error and can try again, or tell the member
        return ToolMessage(content=f"Error: {e}", tool_call_id=call["id"])


def agent_loop(model, messages: list, tools: list, max_steps: int = 5) -> AIMessage:
    """Calls the model with the tools until it answers without asking for one (or max_steps is reached)."""
    tools_by_name = {t.name: t for t in tools}
    model_with_tools = model.bind_tools(tools)
    for _ in range(max_steps):
        reply = model_with_tools.invoke(messages)
        messages.append(reply)
        if not reply.tool_calls:
            return reply
        for call in reply.tool_calls:
            messages.append(run_tool_call(call, tools_by_name))
    raise RuntimeError("the agent did not finish in max_steps")
