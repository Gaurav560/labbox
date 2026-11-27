:::step{type=story title="Everyone wants your tools"}
News travels inside a customer. By week four, Deccan Shield's IT team has heard about `get_policy`, and they have a
request. They already use an AI assistant for internal questions, and they would like it to look up policies too. The
call-centre team would like the same in their tool. And someone wants to try it from Claude Desktop.

You could write the tool three more times, once for each program, in each program's own format. Or you could offer it
**once**, in a standard way that all of them understand.

That standard exists: the **Model Context Protocol (MCP)**. An MCP **server** offers tools (and other things) over a
documented protocol; any MCP **client** (an assistant, an IDE, a chat app) can list them and call them. Anthropic's
FDE job postings name MCP servers among the things FDEs build for customers.

In this chapter Claimdesk becomes an MCP server with two tools. And because of what you saw in chapter 11, the second
tool answers "is this policy in force on this date?" with code, not with a model's judgement.

:::mission
Offer Claimdesk's policy lookup and an exact "in force" check as MCP tools, with errors the client can read and internals
it cannot.
:::
:::

:::step{type=concept title="Servers, clients and tools"}
MCP separates two roles:

| Role | What it is | Here |
|---|---|---|
| Server | a program that offers **tools** (functions), **resources** (data to read) and **prompts** | `server.py`: Claimdesk |
| Client | a program, usually inside an AI app, that connects to servers and lets its model use their tools | `try_server.py`, Deccan Shield's assistant, Claude Desktop |

They talk in **JSON-RPC** messages (a simple request and response format in JSON) over a **transport**:

- **stdio**: the client starts the server as a separate process and they talk over its standard input and output. This is
  what `try_server.py` does. Good for tools on one machine.
- **HTTP**: the server runs as a web service, for tools shared across a network.

When a client connects, it asks the server **which tools it has**. The server answers with each tool's name, description
and input schema, built from your Python code: the function name, its docstring and its type hints. That is why the
docstring matters so much: it is what every client shows to its model.

Check yourself: who runs `get_policy`, the client or the server? The server, in its own process, with its own database
access. The client only asks.

:::diagram{name="fde-mcp"}
One session between a client and Claimdesk's server, with the outputs you will see at the end of this chapter.
:::
:::

:::step{type=history title="One protocol, many tools"}
:::before{title="Before: every editor, every language"}
Before 2016, every code editor needed its own plugin for every programming language: autocomplete for Python in one
editor, again for Python in another, again for Go. M editors and N languages meant M x N plugins.
:::

In 2016 Microsoft published the **Language Server Protocol** (LSP): a language's tools run as one server, and any editor
that speaks the protocol can use it. M x N became M + N.

In November 2024, **Anthropic** introduced the **Model Context Protocol** as an open standard, explicitly inspired by LSP,
for connecting AI applications to tools and data. Its documentation compares it to a USB-C port: one connector, many
devices.

Think of this cable and socket: the same USB-C plug charges a phone, a laptop and a tablet, so a device maker builds one
socket and works with every cable. MCP aims for the same thing between AI apps and tools: Claimdesk builds one server,
and every MCP client can plug in.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-usbc.webp" alt="A close-up of a USB-C cable plug held just above the matching USB-C socket on the edge of a tablet." credit="Wikideas1" license="CC0" source="https://commons.wikimedia.org/wiki/File:USB-C_connector_and_receptacle.webp"}
A USB-C plug and socket: one shape for many devices.
:::

Other AI companies added support in 2025, and today servers exist for databases, ticketing systems, file stores
and much more.

:::solved
Write a tool once as an MCP server; every MCP client can use it.
:::

:::timeline
- **2016** Microsoft publishes the Language Server Protocol.
- **November 2024** Anthropic introduces MCP.
- **2025** Other major AI platforms add MCP support.
- **Today** Enterprises run MCP servers in front of their internal systems.
:::

:::funfact
LSP and MCP both use JSON-RPC 2.0, a specification from 2010 that fits on a few pages.
:::
:::

:::step{type=example title="Worked example: a tiny MCP server"}
This is only to read; it is not in your project. The official Python SDK makes a server out of plain functions:

```python
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("library")

@mcp.tool()
def books_on_shelf(shelf: str) -> list[str]:
    """Titles on one shelf, like S-4."""
    return SHELVES.get(shelf, [])

if __name__ == "__main__":
    mcp.run()
```

- `MCPServer("library")` creates a server with a name clients will show.
- `@mcp.tool()` registers the function as a tool. Its **name** becomes the tool name, its **docstring** the description,
  its **type hints** the input schema (`shelf` is a string) and the output type.
- `mcp.run()` starts the server on stdio, waiting for a client.

From the client side (`mcp.client.Client`), listing and calling look like this:

```python
async with Client(StdioServerParameters(command="python", args=["server.py"])) as client:
    tools = (await client.list_tools()).tools
    result = await client.call_tool("books_on_shelf", {"shelf": "S-4"})
```

`async with` starts the server process, connects, and closes it at the end. `await` waits for each answer.
:::

:::step{type=predict title="Guess first"}
:::question
`try_server.py` starts the starter's `server.py` (no tools registered yet) and calls `get_policy`. What does it get?
:::
- [ ] The policy, because `_policy` exists in the file
- [x] An error: the server does not offer a tool called get_policy
- [ ] The client crashes
:::explain
A function is not a tool until you register it with `@mcp.tool()`. The client only sees what the server offers.
:::
:::

:::step{type=try title="A server with nothing to offer"}
```text
$ python try_server.py
...
get_policy {'policy_no': 'DS-POL-40185'} -> error=True Unknown tool: get_policy
in_force {'policy_no': 'DS-POL-40185', 'on': '2026-10-04'} -> error=True Unknown tool: in_force
...
```

The server starts and answers, but has no tools. Note the shape of a failure: the client did not crash; it got a result
with `is_error=True` and a message. That is how MCP reports problems.
:::

:::step{type=task task=mcp_tools title="Your turn: two tools over MCP"}
In `server.py`, below the TODO:

1. `get_policy(policy_no: str) -> dict`: return `_policy(policy_no)`.
2. `in_force(policy_no: str, on: str) -> bool`: get the policy and return `start_date <= on <= end_date`. Dates written
   `YYYY-MM-DD` compare correctly as text (chapter 4).
3. Put `@mcp.tool()` above each, and give each a docstring that says what it returns and the input format.

Leave unknown policies for the next task. Press **Check**.
:::

:::step{type=concept title="Errors the client should see, and errors it should not" file="12-mcp-server/server.py" line="20-25"}
What should happen when someone asks for `DS-POL-99999`?

Returning `None` is the chapter 11 mistake again: the client's model gets nothing and may fill the gap. The answer must be
an **error result** with a useful message.

The SDK makes a deliberate distinction, and it is a security one. We tried both kinds of exception in the lab image:

```text
a True Error executing tool a: No policy DS-POL-1
b True Error executing tool b
```

- Tool `a` raised **`ToolError("No policy DS-POL-1")`**: the client receives that message. `ToolError` means "a problem
  the caller should know about".
- Tool `b` raised an ordinary **`ValueError`** with the same text: the client receives only "Error executing tool b".
  Unexpected exceptions are hidden, because their messages can contain internals (file paths, SQL, other customers'
  data) that must not leak to whoever is calling.

So: raise `ToolError` for the expected problems you want the caller to read ("No policy DS-POL-99999"), and let
everything else stay hidden and logged on the server.
:::

:::step{type=task task=tool_errors title="Your turn: clear errors for unknown policies"}
In both tools, when `_policy` returns `None`, raise `ToolError(f"No policy {policy_no}")`.

Press **Check**.
:::

:::step{type=try title="Claimdesk, as a server"}
```text
$ python try_server.py
tool get_policy: Looks up a Deccan Shield motor policy by number (like DS-POL-40185): holder, vehicle_reg, vehicle, start_date,
tool in_force: True when the policy covers the date `on` (YYYY-MM-DD): on or after start_date and on or before end_date.
get_policy {'policy_no': 'DS-POL-40185'} -> error=False {
  "policy_no": "DS-POL-40185",
  "holder": "F. Shaikh",
  "vehicle_reg": "MH12GH9012",
  "vehicle": "car",
  "start_date": "2026-04-01",
  "end_date": "2027-03-31",
  "sum_insured": 650000,
  "deductible": 2000
}
in_force {'policy_no': 'DS-POL-40185', 'on': '2026-10-04'} -> error=False true
in_force {'policy_no': 'DS-POL-40925', 'on': '2026-10-26'} -> error=False false
get_policy {'policy_no': 'DS-POL-99999'} -> error=True Error executing tool get_policy: No policy DS-POL-99999
```

Look at the second line from the end, and the line before it. DS-POL-40185 on 4 October 2026: **true**. That is the
question the model got wrong in chapter 11 with the same data in front of it. Here, code answers, and code is right every
time. DS-POL-40925 ended on 20 October, so 26 October is **false**, also exact.

Now Deccan Shield's assistant, the call-centre tool and Claude Desktop can all use these two tools by connecting to one
server. Write once, use everywhere, with the exact checks living in one place.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does the SDK hide the message of an ordinary exception from the client?
:::
- [ ] To save bandwidth
- [x] Unexpected errors can contain internal details (paths, SQL, data) that must not leak to callers
- [ ] Clients cannot display long messages
:::explain
Expected problems are raised as ToolError on purpose, with a message written for the caller. Everything else stays on
the server, in its logs.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does a client learn about a tool when it connects?
:::
- [x] Its name, description (the docstring) and input schema (from the type hints)
- [ ] Its source code
- [ ] Only its name
:::explain
That is all a model sees. A precise docstring is the difference between a tool used well and a tool used wrongly.
:::
:::

:::step{type=deep-dive title="Go deeper: MCP servers at a customer"}
**Authentication.** A stdio server inherits the access of whoever starts it. An HTTP server shared across a network
needs proper authentication (the MCP specification describes OAuth-based authorization for remote servers).

**Read before write.** Start with read-only tools. Tools that change things (pay, cancel, email a customer) need
confirmation steps and audit logs, and often a human (chapter 19).

**Resources and prompts.** MCP servers can also offer read-only data (for example the policy wording of chapter 10 as a
resource) and ready-made prompts, which clients can show in their menus.

**Treat tool results as data.** A client's model reads what your tools return. Never put text from a customer's email
into a tool description, and treat text from other servers as untrusted (the next chapters show why).
:::

:::step{type=recap}
You can now:

- explain MCP: servers offering tools, clients calling them, over stdio or HTTP;
- turn Python functions into MCP tools with `@mcp.tool()`, docstrings and type hints;
- return errors the caller can act on with `ToolError`, and know why other errors are hidden;
- move exact decisions, like "in force on this date", out of the model and into a tool.

Next, chapter 13: Friday of week five, the demo. Put extraction, the policy check and the rules together behind one web
endpoint.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-12-notes.webp" alt="Handwritten notes about an MCP server: MCP lets any client use your tools. Name, docstring and type hints become the tool. The server runs the tool, the client asks. ToolError messages reach the client. Other errors stay hidden on the server. In force on 4 October: code said true." ai="true"}
One page of notes for this chapter.
:::
:::
