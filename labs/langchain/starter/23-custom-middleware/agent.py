"""Middleware you write yourself: a prompt made for each member, and an audit log of every tool call."""
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt, wrap_tool_call

from coop_tools import mandi_price, storage_cost

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Use your tools for rates and charges; never calculate or guess them yourself."
AUDIT: list[str] = []


@dataclass
class Member:
    member_id: str
    name: str
    language: str  # "English" or "Marathi"


@dynamic_prompt
def member_prompt(request: ModelRequest) -> str:
    """Runs before every model call: the system prompt, made for the member who is asking."""
    member = request.runtime.context
    # TODO (task member_prompt): return SYSTEM followed by f" You are talking to {member.name}. Answer in
    #   {member.language}."
    return SYSTEM


@wrap_tool_call
def audit_tools(request, handler):
    """Wraps every tool call: writes it to the audit log, then lets it run."""
    # TODO (task audit_tools): append f"{member id} {tool name} {args}" to AUDIT (the member id is
    #   request.runtime.context.member_id; name and args are in request.tool_call), then run the tool: return
    #   handler(request).
    return handler(request)


def navin_agent():
    return create_agent("openai:ai-chat", tools=[mandi_price, storage_cost], context_schema=Member,
                        middleware=[member_prompt, audit_tools])
