:::step{type=story title="Tools for every app, not only Navin"}
The co-op's tools live inside Navin's Python code. Now others want them: the manager's desktop AI assistant, a
volunteer's coding assistant, maybe next year a WhatsApp bot written by a different team in a different language.
Copying `mandi_price` and `storage_cost` into each would mean three copies to keep correct when a rate or a charge
changes.

The **Model Context Protocol** (MCP) solves this: the co-op runs its tools as an **MCP server**, and any **MCP client**
(an AI app, an IDE, an agent) can list and call them. You write the tools once, with **FastMCP**, and Navin becomes one
client among many.

:::mission
Serve the co-op's tools as an MCP server with FastMCP, then give Navin the server's tools through LangChain's MCP adapter.
:::
:::

:::step{type=history title="One protocol instead of N times M integrations"}
:::before{title="Every app, every tool, its own glue"}
With N AI applications and M tools, each pair needed its own integration code: N times M pieces of glue, each written
differently.
:::

Developer tools had the same problem with programming languages until Microsoft published the **Language Server
Protocol** in **2016**: one protocol between editors and language tools. On **25 November 2024** Anthropic published the
**Model Context Protocol**, built on the same idea for AI: a server offers tools (and resources and prompts) over
JSON-RPC, and any client can use them. Within months it was supported by most AI apps and frameworks. In **December
2024** Jeremiah Lowin released **FastMCP**, a Pythonic way to write servers with decorators; its first version became
part of the official MCP Python SDK.

:::solved
**Write a tool once, use it everywhere.** N plus M pieces instead of N times M.
:::

:::timeline
- **2016** Language Server Protocol.
- **2024** MCP (November) and FastMCP (December).
- **2025** MCP supported across AI apps and frameworks.
:::
:::

:::step{type=concept title="A server in a few lines" file="21-mcp/coop_server.py" line="1-20"}
```python
from fastmcp import FastMCP

mcp = FastMCP("pimpalgaon-coop")

@mcp.tool
def storage_cost(crates: int, days: int) -> int:
    """The cold storage charge in rupees for some crates kept some days (Rs 2 per crate per day)."""
    return crates * days * 2

if __name__ == "__main__":
    mcp.run()        # stdio: talk over standard input and output
```

It looks like chapter 12's `@tool`, on purpose: the name, the docstring and the type hints become the tool's
description, exactly as before. The difference is who can call it: anything that speaks MCP.

:::diagram{name="lc-mcp"}
The adapter starts the server, lists its tools, and the agent calls them over MCP until the block ends.
:::

| Transport | How a client reaches the server | Use for |
|---|---|---|
| **stdio** | the client starts the server as a child process | tools on the same machine (this chapter) |
| **Streamable HTTP** | the server runs as a web service | tools shared by many clients over a network |
:::

:::step{type=task task=mcp_server title="Your turn: the co-op's MCP server" file="21-mcp/coop_server.py" line="8-16"}
Offer both functions as MCP tools: put `@mcp.tool` on the line above each `def` (and remove the TODO comment).

Press **Check**.
:::

:::step{type=concept title="Navin as an MCP client" file="21-mcp/client.py" line="11-17"}
LangChain 1.x has MCP built in, as `langchain.mcp` (still marked **beta**, so it prints a warning and its API may
change). `MCPAdapter` connects to a server and turns its tools into LangChain tools:

```python
async with MCPAdapter(Path("coop_server.py")) as adapter:   # a path: start it over stdio
    tools = await adapter.list_tools()                       # the server's tools, as LangChain tools
    agent = create_agent("openai:ai-chat", tools=tools, ...)
    result = await agent.ainvoke({...})                      # async: MCP calls are network calls
```

Everything happens inside `async with`: when the block ends, the adapter closes the connection and stops the server
process. The adapter also accepts a URL (a Streamable HTTP server) or a FastMCP object in the same process, which is
handy in tests.
:::

:::step{type=task task=mcp_agent title="Your turn: tools from the server" file="21-mcp/client.py" line="11-17"}
Finish `ask_over_mcp(question)`: inside `async with MCPAdapter(SERVER) as adapter`, list the tools, build the agent with
them and `system_prompt=SYSTEM`, run it with `await agent.ainvoke(...)`, and return the tool names and the last
message's content.

```bash run
cd /workspace/21-mcp && python main.py
```

Press **Check**.
:::

:::step{type=try title="Two tools from another process"}
```text
$ python main.py
  from langchain.mcp import MCPAdapter
tools from the server: ['mandi_price', 'storage_cost']
The rate for grapes is ₹4600 per quintal. Storing 15 crates for 4 days will cost you ₹120.
```

(The first line is the end of the beta warning, which names the import that triggered it.)

Navin's code contains no co-op tool at all. `MCPAdapter` started `coop_server.py` as a separate process, listed its two
tools, and the agent called them over MCP: ₹4,600 from the server's rate table and ₹120 from its arithmetic (15 × 4 ×
2). The manager's desktop assistant could use the very same server with one line of configuration, and when the storage
charge changes, it changes in one place.
:::

:::step{type=predict title="Guess first"}
:::question
A server prints debugging output with `print(...)`. It runs over stdio. What can happen?
:::
- [ ] Nothing: prints go to the terminal
- [x] The client receives text that is not MCP and the connection breaks
- [ ] The prints appear in the model's answer
:::explain
On stdio, standard output **is** the connection. Log to standard error (FastMCP's own banner and logs go there).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does a stdio MCP client need to use a server?
:::
- [x] The command (or file) that starts it
- [ ] The server's source code inside its own program
- [ ] A shared database
:::explain
The client starts the server and speaks MCP over its standard input and output.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why must the agent run inside `async with MCPAdapter(...)`?
:::
- [ ] For speed
- [x] The tools call the server through the adapter's connection, which closes when the block ends
- [ ] Because agents are always async
:::explain
Outside the block the server process has stopped, so a tool call would have nothing to talk to.
:::
:::

:::step{type=deep-dive title="Go deeper: MCP in production"}
**HTTP servers.** `mcp.run(transport="http")` serves the same tools as a web service; clients connect with a URL. Then
it is an API on a network: authenticate clients (the docs' MCP "Authentication" page) and rate-limit.

**Only the tools you need.** A server may offer many tools. Give an agent only those it needs: fewer tools, fewer wrong
choices, and fewer tokens spent on tool descriptions.

**Tools that change data.** A booking tool served over MCP can be called by any client: check its arguments on the
server, not in the client.
:::

:::step{type=recap}
You can now:

- explain MCP and why one protocol beats N times M integrations;
- write an MCP server with FastMCP and `@mcp.tool`;
- use a server's tools from a LangChain agent with `MCPAdapter`;
- keep a stdio server's standard output clean.

That ends Part 4. Next, chapter 22: middleware, the hooks that make an agent production-ready.

:::photo{src="/lesson-images/langchain/lc-21-notes.webp" alt="Handwritten notes about MCP: MCP: one protocol for tools; FastMCP: @mcp.tool; stdio: the client starts it; MCPAdapter gives tools; stdout is the wire" ai="true"}
One page of notes for this chapter.
:::
:::
