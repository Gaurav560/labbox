import r
from fake_openai import Reply


def test_loan_tool():
    def check():
        from langchain_core.tools import BaseTool
        from member_tools import crop_loan_limit
        if not isinstance(crop_loan_limit, BaseTool):
            return r.failed("loan_tool", "crop_loan_limit is still a plain function: decorate it with @tool so the model can see it.")
        if "50,000" not in (crop_loan_limit.description or ""):
            return r.failed("loan_tool", "Give it the docstring from the TODO: the model reads it to know when to call the tool.", "...(Rs 50,000 per acre).", crop_loan_limit.description)
        if crop_loan_limit.args.get("acres", {}).get("type") != "number":
            return r.failed("loan_tool", "Keep the type hint acres: float, so the model is told to send a number.")
        got = crop_loan_limit.invoke({"acres": 2.5})
        if got != 125000:
            return r.failed("loan_tool", "Return int(acres * 50000).", 125000, got)
        r.passed("loan_tool", "The docstring became the description, the type hint the schema: that is all the model sees of your function.")
    r.task("loan_tool", check)


def test_member_tool(fake):
    def check():
        from agent import navin_agent
        from member_tools import Member
        fake.script = lambda b: Reply.tool("my_storage", {}) if len(fake.chat_requests) == 1 else Reply("ok")
        try:
            agent = navin_agent()
        except ValueError as e:
            if "docstring" in str(e):
                return r.failed("member_tool", "The agent cannot be built yet: crop_loan_limit has no docstring. Finish the loan tool first (the task above).")
            raise
        agent.invoke({"messages": [{"role": "user", "content": "my crates?"}]}, context=Member("M-104"))
        if "my_storage" not in fake.tool_names(fake.chat_requests[0]):
            return r.failed("member_tool", "The agent was not offered my_storage.")
        if fake.chat_requests[0]["tools"][fake.tool_names(fake.chat_requests[0]).index("my_storage")]["function"]["parameters"].get("properties"):
            return r.failed("member_tool", "my_storage must take no parameters the model fills in: the runtime argument is hidden from the model.")
        results = [m["content"] for m in fake.chat_requests[-1]["messages"] if m["role"] == "tool"]
        if results != ["Ravi Patil has 40 crates in cold storage."]:
            return r.failed("member_tool", "Look the member up with runtime.context.member_id and return f\"{name} has {crates} crates in cold storage.\"",
                            "Ravi Patil has 40 crates in cold storage.", results)
        r.passed("member_tool", "The app says who is asking, through the context; the model cannot change it, so Ravi never sees Asha's crates.")
    r.task("member_tool", check)
