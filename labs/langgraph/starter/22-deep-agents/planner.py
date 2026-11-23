"""A deep agent that writes the board's monsoon readiness plan: it plans, reads the data, and delegates counting."""
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware.filesystem import FilesystemPermission
from langchain.chat_models import init_chat_model
from langchain_core.rate_limiters import InMemoryRateLimiter

from analysis import count_complaints

PLANNER = ("You prepare the Ujjwal Nagar Water Board's monsoon readiness plan. Read /pipes.csv and /crews.md. You may not "
           "read /complaints_2025.csv: ask the data-analyst for every number about complaints. Write the plan to "
           "/plan.md: the streets that need work before June, why (with numbers and pipe ages), which crew, and in "
           "what order. At most 250 words.")
NO_RAW_DATA = [FilesystemPermission(operations=["read"], paths=["/complaints_2025.csv"], mode="deny")]
ANALYST = {
    "name": "data-analyst",
    "description": "Answers questions about complaints_2025.csv with exact counts by street, kind and month.",
    "system_prompt": "You answer questions about the board's complaints with the count_complaints tool. Report exact numbers.",
    # TODO (task analyst_subagent): give the analyst its tool: "tools": [count_complaints].
}


LIMITER = InMemoryRateLimiter(requests_per_second=0.3, check_every_n_seconds=0.1, max_bucket_size=4)


def model():
    """The chat model, shared limiter included: at most about 18 calls a minute (the gateway allows 20)."""
    return init_chat_model("openai:ai-chat", temperature=0, rate_limiter=LIMITER)


def build_agent(root: str = "data"):
    # TODO (task deep_agent): also pass subagents=[ANALYST], and backend=FilesystemBackend(root_dir=root,
    #   virtual_mode=True) so the agent's files are the real files in data/ (and nothing outside it).
    return create_deep_agent(model=model(), system_prompt=PLANNER, permissions=NO_RAW_DATA)
