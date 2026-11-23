"""An agent, by hand: the model may ask for tools; we run them and send the results back, until it answers."""
from langchain.messages import AIMessage, ToolMessage


def run_tool_call(call: dict, tools_by_name: dict) -> ToolMessage:
    """Runs one tool call the model asked for, and wraps the result for the model."""
    # TODO (task run_tool_call): find the tool by call["name"] in tools_by_name, run it with tool.invoke(call["args"]),
    #   and return ToolMessage(content=str(result), tool_call_id=call["id"]). If the tool raises an exception, return a
    #   ToolMessage with content "Error: " plus the exception's text instead, so the model can read what went wrong.
    return ToolMessage(content="", tool_call_id=call["id"])


def agent_loop(model, messages: list, tools: list, max_steps: int = 5) -> AIMessage:
    """Calls the model with the tools until it answers without asking for one (or max_steps is reached)."""
    tools_by_name = {t.name: t for t in tools}
    model_with_tools = model.bind_tools(tools)
    # TODO (task agent_loop): repeat at most max_steps times: reply = model_with_tools.invoke(messages); add reply to
    #   messages; if reply.tool_calls is empty, return reply; otherwise add run_tool_call(...) for every call in
    #   reply.tool_calls. If the steps run out, raise RuntimeError("the agent did not finish in max_steps").
    return model_with_tools.invoke(messages)
