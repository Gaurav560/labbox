"""Navin with built-in middleware: tool errors the model can read, a ceiling on model calls, and summaries."""
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, SummarizationMiddleware, ToolErrorMiddleware
from langgraph.checkpoint.memory import InMemorySaver

from coop_tools import mandi_price, storage_cost

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Use your tools for rates and charges; never calculate or guess them yourself."


def on_tool_error(error: Exception, request) -> str | None:
    """Decides which tool errors the model may see. Everything else stops the run."""
    # TODO (task tool_errors): for a ValueError (a member's mistake, like an unknown crop) return
    #   f"{request.tool_call['name']} failed: {error}", so the model can explain it. For any other exception return
    #   None: the run stops, and internal details never reach the model or the member.
    return None


def navin_agent():
    return create_agent(
        "openai:ai-chat",
        tools=[mandi_price, storage_cost],
        system_prompt=SYSTEM,
        checkpointer=InMemorySaver(),
        # TODO (task limits_and_summaries): add middleware=[...] with, in this order:
        #   ToolErrorMiddleware(on_tool_error),
        #   ModelCallLimitMiddleware(run_limit=5, exit_behavior="end"),
        #   SummarizationMiddleware("openai:ai-chat", trigger=("messages", 8), keep=("messages", 4)).
    )
