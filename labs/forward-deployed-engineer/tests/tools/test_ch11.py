import json

import r
from fake_openai import Reply


def test_policy_tool():
    def check():
        import agent
        if len(agent.TOOLS) != 1:
            return r.failed("policy_tool", "TOOLS should describe exactly one tool, get_policy.", 1, len(agent.TOOLS))
        fn = agent.TOOLS[0].get("function", {})
        params = fn.get("parameters", {})
        if agent.TOOLS[0].get("type") != "function" or fn.get("name") != "get_policy" or params.get("required") != ["policy_no"] \
                or (params.get("properties", {}).get("policy_no", {}).get("type") != "string"):
            return r.failed("policy_tool", "The tool is {\"type\": \"function\", \"function\": {\"name\": \"get_policy\", \"description\": ..., \"parameters\": "
                            "an object schema with a string property policy_no, required}}.", "get_policy(policy_no: string)", agent.TOOLS[0])
        if len(fn.get("description", "")) < 40 or "DS-POL" not in fn.get("description", ""):
            return r.failed("policy_tool", "Describe the tool for the model: what it returns, and the format of a policy number (DS-POL-12345).")
        got = json.loads(agent.run_tool("get_policy", json.dumps({"policy_no": "DS-POL-40185"})))
        if got.get("vehicle_reg") != "MH12GH9012" or got.get("deductible") != 2000:
            return r.failed("policy_tool", "run_tool(\"get_policy\", ...) should return the policy as JSON text: json.loads the arguments and call get_policy.",
                            "MH12GH9012, deductible 2000", got)
        missing = json.loads(agent.run_tool("get_policy", json.dumps({"policy_no": "DS-POL-99999"})))
        if "error" not in missing:
            return r.failed("policy_tool", "For an unknown policy return {\"error\": ...}: the model must be told it does not exist, not given null.", "an error", missing)
        if "error" not in json.loads(agent.run_tool("delete_policy", "{}")):
            return r.failed("policy_tool", "A tool name you do not have must return an error, never run something else.")
        r.passed("policy_tool", "The model can now ask for a policy by number, and only that: one tool, one clear job.")
    r.task("policy_tool", check)


def test_tool_loop(fake):
    def check():
        import agent
        fake.script = lambda b: (Reply.tool("get_policy", {"policy_no": "DS-POL-40185"}) if len(fake.chat_requests) == 1
                                 else Reply("Yes, it is in force; the deductible is Rs 2,000."))
        answer, calls = agent.run_agent("Is DS-POL-40185 in force?")
        if len(fake.chat_requests) < 2:
            return r.failed("tool_loop", "After the model asks for get_policy, run it and call the model again with the result.", 2, len(fake.chat_requests))
        msgs = fake.chat_requests[-1].get("messages", [])
        tool_msgs = [m for m in msgs if m.get("role") == "tool"]
        if not tool_msgs or "MH12GH9012" not in str(tool_msgs[0].get("content")) or tool_msgs[0].get("tool_call_id") != "call_1":
            return r.failed("tool_loop", "Append the assistant message, then {\"role\": \"tool\", \"tool_call_id\": call.id, \"content\": run_tool(...)} for each call.",
                            "a tool message with the policy", tool_msgs)
        if not fake.chat_requests[0].get("tools"):
            return r.failed("tool_loop", "Offer the tools on every call: tools=TOOLS.")
        if answer != "Yes, it is in force; the deductible is Rs 2,000." or calls != [("get_policy", json.dumps({"policy_no": "DS-POL-40185"}))]:
            return r.failed("tool_loop", "Return the final message's content, and the list of (name, arguments) of the calls made.",
                            ("the answer", [("get_policy", '{"policy_no": "DS-POL-40185"}')]), (answer, calls))
        fake.reset()
        fake.script = lambda b: Reply.tool("get_policy", {"policy_no": "DS-POL-40185"})
        answer, calls = agent.run_agent("loop forever", max_turns=4)
        if len(fake.chat_requests) != 4 or answer != "Stopped after 4 model calls without an answer.":
            return r.failed("tool_loop", "A model that keeps asking for tools must be stopped: after max_turns calls, return the stop message.",
                            "4 calls, then 'Stopped after 4 model calls without an answer.'", f"{len(fake.chat_requests)} calls, {answer!r}")
        r.passed("tool_loop", "The model decides what to look up; your loop decides how far it may go. Both matter.")
    r.task("tool_loop", check)
