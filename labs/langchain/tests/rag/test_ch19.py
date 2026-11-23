import r
from fake_openai import Reply


def test_rules_tool(fake):
    def check():
        import rag
        rag.rule_store.cache_clear()
        got = rag.search_rules.invoke({"query": "onion storage crates"})
        if not got or got == "No rule found for that question.":
            return r.failed("rules_tool", "search_rules found nothing for a storage question. Return the found pieces, each as "
                            "f\"[{source}] {text}\", joined by a blank line.")
        if "[storage.txt]" not in got:
            return r.failed("rules_tool", "Start each piece with its source in brackets, like [storage.txt], so the model can cite it.", "[storage.txt] Cold storage...", got[:80])
        nothing = rag.search_rules.invoke({"query": "the capital of France"})
        if nothing != "No rule found for that question.":
            return r.failed("rules_tool", "When search finds nothing above the threshold, return \"No rule found for that question.\"",
                            "No rule found for that question.", nothing[:80])
        r.passed("rules_tool", "A retrieval tool: the model asks for rules, gets only the pieces that match, each with its source.")
    r.task("rules_tool", check)


def test_rag_agent(fake):
    def check():
        import rag
        rag.rule_store.cache_clear()
        agent = rag.rag_agent()
        if agent is None:
            return r.failed("rag_agent", "rag_agent() returned None. Return create_agent(\"openai:ai-chat\", tools=[search_rules, mandi_price, storage_cost], system_prompt=SYSTEM).")
        fake.script = lambda b: Reply.tool("search_rules", {"query": "onion storage crates"}) if len(fake.chat_requests) == 1 else Reply("Yes [storage.txt].")
        result = agent.invoke({"messages": [{"role": "user", "content": "Can I store 80 crates of onions?"}]})
        first = fake.chat_requests[0]
        if sorted(fake.tool_names(first)) != ["mandi_price", "search_rules", "storage_cost"]:
            return r.failed("rag_agent", "Give the agent search_rules and the two co-op tools.", "['mandi_price', 'search_rules', 'storage_cost']", fake.tool_names(first))
        if fake.texts(first, "system") != [rag.SYSTEM]:
            return r.failed("rag_agent", "Pass system_prompt=SYSTEM: it tells Navin to answer only from the rules and to cite them.")
        tool_text = [m["content"] for m in fake.chat_requests[-1]["messages"] if m["role"] == "tool"]
        if not tool_text or "[storage.txt]" not in tool_text[0]:
            return r.failed("rag_agent", "The rule pieces should reach the model as the tool's result.")
        r.passed("rag_agent", "Retrieval as a tool: the model decides when to look in the rule book, and answers from what it found.")
    r.task("rag_agent", check)
