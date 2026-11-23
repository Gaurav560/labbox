import r
from fake_openai import Reply


def test_member_prompt(fake):
    def check():
        from agent import SYSTEM, Member, navin_agent
        fake.script = lambda b: Reply("ok")
        navin_agent().invoke({"messages": [{"role": "user", "content": "hi"}]}, context=Member("M-104", "Ravi", "Marathi"))
        system = fake.texts(fake.chat_requests[-1], "system")
        want = SYSTEM + " You are talking to Ravi. Answer in Marathi."
        if system != [want]:
            return r.failed("member_prompt", "Return SYSTEM followed by \" You are talking to {name}. Answer in {language}.\"", want, system)
        r.passed("member_prompt", "One agent, a prompt made for each member: Ravi gets Marathi, Asha gets English.")
    r.task("member_prompt", check)


def test_audit_tools(fake):
    def check():
        import agent as ag
        ag.AUDIT.clear()
        fake.script = lambda b: Reply.tool("storage_cost", {"crates": 25, "days": 8}) if len(fake.chat_requests) == 1 else Reply("Rs 400.")
        result = ag.navin_agent().invoke({"messages": [{"role": "user", "content": "cost?"}]}, context=ag.Member("M-221", "Asha", "English"))
        if ag.AUDIT != ["M-221 storage_cost {'crates': 25, 'days': 8}"]:
            return r.failed("audit_tools", "Append f\"{member id} {tool name} {args}\" to AUDIT for each tool call.",
                            ["M-221 storage_cost {'crates': 25, 'days': 8}"], ag.AUDIT)
        tools = [m["content"] for m in fake.chat_requests[-1]["messages"] if m["role"] == "tool"]
        if tools != ["400"]:
            return r.failed("audit_tools", "After logging, run the tool: return handler(request).", ["400"], tools)
        r.passed("audit_tools", "Every tool call is logged with who asked, before it runs, without touching a single tool.")
    r.task("audit_tools", check)
