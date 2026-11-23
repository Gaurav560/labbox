"""Navin as a web service: members chat, and the manager approves bookings."""
from fastapi import FastAPI
from langgraph.types import Command
from pydantic import BaseModel

from navin import Member, navin_agent

app = FastAPI(title="Navin, the Pimpalgaon co-op help desk")
agent = navin_agent()
NAMES = {"M-104": "Ravi Patil", "M-221": "Asha Shinde"}


class ChatIn(BaseModel):
    member_id: str
    message: str


class Decision(BaseModel):
    member_id: str
    decision: dict


def reply(result: dict) -> dict:
    """An answer, or a booking that waits for the manager."""
    if result.get("__interrupt__"):
        request = result["__interrupt__"][0].value["action_requests"][0]
        return {"status": "waiting_for_manager", "action": request["name"], "args": request["args"]}
    return {"status": "answered", "answer": result["messages"][-1].content}


@app.post("/chat")
def chat(body: ChatIn) -> dict:
    # TODO (task chat_endpoint): run the agent for this member: invoke it with the message, the config
    #   {"configurable": {"thread_id": body.member_id}} and context=Member(body.member_id, NAMES.get(body.member_id,
    #   "a member")), and return reply(result).
    return {"status": "answered", "answer": ""}


@app.post("/manager/decide")
def decide(body: Decision) -> dict:
    config = {"configurable": {"thread_id": body.member_id}}
    member = Member(body.member_id, NAMES.get(body.member_id, "a member"))
    result = agent.invoke(Command(resume={"decisions": [body.decision]}), config, context=member)
    return reply(result)
