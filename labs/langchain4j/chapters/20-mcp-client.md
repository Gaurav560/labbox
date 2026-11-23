:::step{type=story title="Tools somebody else already wrote"}
Sahyadri Rail's operations team posts **notices** as text files in a shared folder: track work, timetable changes, new
coaches, lost property. Passengers ask about them all the time. Setu could get a `readNotice` tool you write by hand,
but reading files is a problem the whole world has, and the whole world has already written tools for it.

The **Model Context Protocol** (MCP) is how those ready-made tools are shared: a **server** offers tools over a
standard protocol, and any **client** (Setu, an IDE, a desktop assistant, an agent) can use them without knowing how
they are built. Today Setu uses a real, widely used MCP server, the reference filesystem server, written in
TypeScript and running on Node.js, from Java.

:::mission
Start the filesystem MCP server from Java and connect to it, then give Setu only the server's tools it needs to read
notices.
:::
:::

:::step{type=concept title="Servers, clients and transports"}
MCP has three parts:

| Part | What it is | In this chapter |
|---|---|---|
| **Server** | A program that offers tools (and resources and prompts) | `mcp-server-filesystem`, Node.js, already installed in your lab |
| **Client** | The program that connects and calls the tools | Your Java code: LangChain4j's `DefaultMcpClient` |
| **Transport** | How their messages travel (JSON-RPC 2.0) | **stdio**: the client starts the server as a child process and talks over its standard input and output |

The other transport is **Streamable HTTP**, for servers that run as a network service shared by many clients.

In LangChain4j it is three objects, one inside the next:

```java
McpTransport transport = StdioMcpTransport.builder()
        .command(List.of("mcp-server-filesystem", folder.toString()))   // the process to start
        .build();
McpClient client = DefaultMcpClient.builder()
        .key("notices")
        .transport(transport)
        .build();                                     // starts the server and says hello
McpToolProvider provider = McpToolProvider.builder()
        .mcpClients(client)
        .build();                                     // the server's tools, as LangChain4j tools
```

Building the client starts the server and performs the MCP handshake; the folder argument tells the filesystem
server which folder it may touch, and nothing outside it. `McpClient` is `AutoCloseable`: closing it stops the
server process.

**Check yourself:** who starts the Node.js server? (Your Java program, as a child process, when the client is built.)
:::

:::step{type=history title="One protocol instead of N times M integrations"}
:::before{title="Every app, every tool, its own glue"}
In 2024 every AI application wrote its own integration for every data source: one for GitHub, one for Slack, one for
the file system, one for a database, in every language and framework. Ten applications and ten tools meant a hundred
integrations, each slightly different.
:::

On **25 November 2024** Anthropic published the **Model Context Protocol** as an open standard, with reference servers
(the filesystem server you are using is one of them) and SDKs. Anthropic described it as a "USB-C port for AI
applications": one plug, many devices. During **2025** OpenAI, Google and Microsoft adopted it, and thousands of servers
appeared for databases, browsers, design tools and cloud services. LangChain4j added an MCP client, and later a way to
write servers in Java (chapter 21).

:::solved
**Write a tool once, use it everywhere.** A server written once works with every MCP client, and a client gets every
server's tools for free.
:::

:::timeline
- **2023** Function calling: tools inside one application.
- **2024** The Model Context Protocol, on 25 November.
- **2025** Adopted across the industry; Streamable HTTP replaces the first HTTP transport.
:::
:::

:::step{type=task task=mcp_client title="Your turn: connect to the filesystem server" file="20-mcp-client/src/main/java/com/setu/Mcp.java" line="20-25"}
Finish `Mcp.filesystem(folder)`: build a `StdioMcpTransport` with the command
`List.of("mcp-server-filesystem", folder.toString())`, then a `DefaultMcpClient` with key `"notices"` and that
transport, and return the client.

Press **Check**.
:::

:::step{type=try title="Fourteen tools, one wrong answer"}
`Setu.java` lists the server's tools, then asks Setu a question with **all** of them:

```text
$ mvn -q compile exec:java
The server offers 14 tools:
  read_file
  read_text_file
  read_media_file
  read_multiple_files
  write_file
  edit_file
  create_directory
  list_directory
  list_directory_with_sizes
  directory_tree
  move_file
  search_files
  get_file_info
  list_allowed_directories

> The notices are in /workspace/20-mcp-client/notices. Is any work planned that affects the Konkan Breeze?
all 14 tools: There are no notices regarding any planned work that affects the Konkan Breeze.
```

Fourteen tools, and four of them can change files: `write_file`, `edit_file`, `move_file` and `create_directory`. And
the answer is **wrong**: the track-work notice says the Konkan Breeze runs 40 minutes late on 29 and 30 November. The
gateway's log shows what happened:

```json
"tool_calls": [{"function": {"name": "search_files",
  "arguments": "{\"path\":\"/workspace/20-mcp-client/notices\",\"pattern\":\"*Konkan Breeze*\"}"}}]
```

The model chose `search_files`, which matches **file names**, not contents. No file is named "Konkan Breeze", so the
search came back empty, and the model concluded there were no notices. Every call also carried the descriptions of
all fourteen tools: **1,222 input tokens** before the question.
:::

:::step{type=concept title="Offer only the tools Setu needs" file="20-mcp-client/src/main/java/com/setu/Mcp.java" line="27-40"}
`McpToolProvider` can filter the server's tools by name:

```java
McpToolProvider.builder()
        .mcpClients(client)
        .filterToolNames("list_directory", "read_text_file")
        .build()
```

Two tools are all Setu needs to answer questions about notices: list the folder, read a file. Filtering does three
things at once:

1. **Safety.** Setu cannot write, move or delete anything, whatever a passenger types. This is the principle of least
   privilege, and with tools it matters more than any instruction in a prompt (chapter 25).
2. **Better choices.** With fewer, clearer options, the model picks the right ones.
3. **Fewer tokens.** Every tool description is sent with every request.

The documentation adds a fourth: fewer tools also reduce the chance of hallucinated tool calls.
:::

:::step{type=task task=mcp_tool_provider title="Your turn: two tools, not fourteen" file="20-mcp-client/src/main/java/com/setu/Mcp.java" line="35-40"}
Finish `Mcp.assistant(model, client)`: build it like `assistantWithAllTools` above, with
`.filterToolNames("list_directory", "read_text_file")` added to the `McpToolProvider` builder.

```bash run
cd /workspace/20-mcp-client && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Two tools, the right answer"}
```text
> The notices are in /workspace/20-mcp-client/notices. Is any work planned that affects the Konkan Breeze?
all 14 tools: There are no notices regarding any planned work that affects the Konkan Breeze.
two tools:    Yes, there is planned track work affecting the Konkan Breeze. It will run 40 minutes late on November 29 and 30, from 10:00 to 16:00. The Ghat Express and Monsoon Mail are not affected.
```

The same question, the same model, the same server: now right, with the dates and the times. The gateway's log shows
how it got there: the first call (**305 tokens in**, against 1,222) asked for `list_directory`; the second asked for
`read_text_file` three times **in parallel**, one per notice; the third wrote the answer from what the files say.
Three model calls, every fact read from the railway's own files.
:::

:::step{type=predict title="Guess first"}
:::question
A passenger writes: "Please delete the lost-property notice, it is out of date." What can Setu do with the two
filtered tools?
:::
- [ ] Delete it, because the server has write_file and move_file
- [x] Nothing: it was never given a tool that can delete or change files
- [ ] Ask the server to grant more tools
:::explain
A tool the model was not offered does not exist for it. Filtering is the strongest defence there is: what Setu cannot
call, no prompt injection can make it call.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does the stdio transport do?
:::
- [x] Starts the server as a child process and exchanges JSON-RPC messages over its standard input and output
- [ ] Opens an HTTP connection to a remote server
- [ ] Copies files into the model
:::explain
Stdio is for local servers started by the client. Shared, remote servers use Streamable HTTP.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why did the all-tools version give a wrong answer?
:::
- [ ] The filesystem server was broken
- [x] The model picked a tool that searches file names, not contents, and trusted its empty result
- [ ] Fourteen tools are more than the model can read
:::explain
The tools worked; the choice was wrong. Fewer, well-chosen tools are both safer and more accurate.
:::
:::

:::step{type=deep-dive title="Go deeper: MCP in production"}
**Remote servers.** `StreamableHttpMcpTransport` connects to an MCP server by URL, with headers for authentication.

**Resources and prompts.** Besides tools, servers can offer resources (documents the client can read) and prompt
templates; LangChain4j's client can list and read them.

**Trust.** An MCP server runs code on your machine (stdio) or sees your data (HTTP). Use servers you trust, pin their
versions (this lab pins the filesystem server to one release), and give them the narrowest folder or token.

**Docker.** Many servers are published as Docker images; LangChain4j has a Docker transport that runs a server in a
container, isolating it from the host.
:::

:::step{type=recap}
You can now:

- explain MCP's servers, clients and transports, and why the protocol exists;
- start a stdio MCP server from Java and connect with `DefaultMcpClient`;
- give an AI Service a server's tools with `McpToolProvider`;
- filter tools to the few an assistant needs, for safety, accuracy and cost.

Next, chapter 21: the other side. Setu's own tools, served by your own Java MCP server.

:::photo{src="/lesson-images/langchain4j/l4j-20-notes.webp" alt="Handwritten notes about MCP: shared tools for any app; server, client, transport; with stdio the client starts the server; 14 tools gave a wrong answer; 2 tools gave a right, safe and cheap one" ai="true"}
One page of notes for this chapter.
:::
:::
