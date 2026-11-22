:::step{type=story title="Everyone wants the museum's facts"}
Atlas's tools are good: real opening hours, real show times, the right date maths. Soon other teams ask for them. The
education office uses an AI assistant on their laptops to plan school visits, and wants it to check show times. A
partner, a city tourism app, wants its own assistant to know when the museum is open. Neither is built with Spring,
and neither should copy your Java code.

What they need is a **standard plug**: a way for any AI application to discover what tools a server offers and call
them, whatever language each side is written in. That standard exists, and it has taken over the AI world in a year:
the **Model Context Protocol**, MCP. In this chapter Atlas becomes an MCP **server**, and any MCP-aware assistant can
use the museum's facts.

The MCP documentation describes it with a picture everyone knows: a USB-C port for AI applications. One plug shape,
and any device works with any computer.

:::photo{src="/lesson-images/spring-ai/usb-c.webp" alt="A hand holding two USB-C plugs side by side, one black and one white" credit="Logant547" license="CC BY 4.0" source="https://commons.wikimedia.org/wiki/File:Two_USB-C_connectors_being_held.jpg"}
A USB-C plug: one shape for every device.
:::

:::mission
Turn Atlas into an MCP server that offers its museum tools to any MCP client.
:::
:::

:::step{type=history title="A protocol for tools"}
In chapter 7 you gave tools to **your own** model. Before MCP, every AI application did that in its own way, so a tool
written for one assistant had to be rewritten for the next.

:::before{title="Before MCP"}
Each assistant (ChatGPT plugins, IDE assistants, chat apps, agent frameworks) had its own format for describing tools
and its own way of calling them. Connecting M assistants to N tools meant M times N little integrations, each
maintained by someone, each slightly different.
:::

In **November 2024**, Anthropic published the **Model Context Protocol** as an open standard: a client (the AI
application) and a server (the one with the tools or data) talk JSON-RPC, a simple message format, over standard
input and output or over HTTP. In 2025 OpenAI, Google and Microsoft adopted it, and thousands of MCP servers appeared:
for files, databases, GitHub, calendars, payment systems.

:::solved
**Write a tool once, use it from any assistant.** M plus N, not M times N. The official Java SDK for MCP began in the
Spring AI team, which is why Spring AI's MCP support is among the most complete: a starter turns your `@Tool` methods
into an MCP server with a few lines of configuration.
:::

:::timeline
- **2024** Anthropic publishes the Model Context Protocol (November).
- **2025** OpenAI, Google and Microsoft adopt MCP; Spring AI 1.0 ships MCP starters; the Streamable HTTP transport arrives.
- **2026** Spring AI 2.1 supports the newest version of the protocol and stateless servers.
:::
:::

:::step{type=concept title="Servers, clients and three kinds of things"}
MCP has two roles:

| Role | Is | Example |
|---|---|---|
| **MCP server** | offers capabilities | Atlas, offering museum tools |
| **MCP client** | inside an AI application; discovers and uses them | the education office's assistant |

A server can offer three kinds of things:

1. **Tools**: functions the model can call (what you built in chapter 7).
2. **Resources**: data the application can read (a file, a document, a database row).
3. **Prompts**: ready-made prompt templates a user can pick.

Messages are **JSON-RPC**: small JSON objects with a `method` (like `tools/list` or `tools/call`), `params`, and an `id`
to match each answer to its question. They travel over one of two **transports**: standard input and output (the
client starts the server as a process on the same machine) or **Streamable HTTP** (the server is a web service at an
address like `/mcp`, which is what Atlas will be).

:::diagram{name="ai-mcp"}
An MCP client asks the server which tools it has, the model picks one, and the client calls it on the server.
:::

**Check yourself:** in MCP terms, which part decides **when** to call `openingHours`? (The model inside the client's AI
application. The server only describes and runs the tool.)
:::

:::step{type=example title="Worked example: the starter and two settings" file="10-mcp/pom.xml"}
`10-mcp/pom.xml` already has the starter for an MCP server on Spring MVC:

```xml
<dependency>
  <groupId>org.springframework.ai</groupId>
  <artifactId>spring-ai-starter-mcp-server-webmvc</artifactId>
</dependency>
```

The server is configured with properties. These are the ones Atlas needs, from Spring AI's reference documentation:

| Property | Means |
|---|---|
| `spring.ai.mcp.server.protocol=STREAMABLE` | serve MCP over Streamable HTTP, at `/mcp` |
| `spring.ai.mcp.server.name=...` | the server's name, shown to clients |
| `spring.ai.mcp.server.version=...` | its version |
| `spring.ai.mcp.server.instructions=...` | a sentence telling clients what the server is for |

Then the tools. The starter offers every **`ToolCallbackProvider`** bean to MCP clients. `MethodToolCallbackProvider`
turns the `@Tool` methods of any object into such a provider:

```java
@Bean
ToolCallbackProvider weatherTools(WeatherService weather) {
    return MethodToolCallbackProvider.builder()
            .toolObjects(weather)
            .build();
}
```

The same `@Tool` annotations from chapter 7, the same descriptions: written once, now usable by Atlas's own model and by
any MCP client.
:::

:::step{type=task task=mcp_server title="Your turn: switch on the MCP server" file="10-mcp/src/main/resources/application.properties" line="11"}
In `10-mcp/src/main/resources/application.properties`, turn on the MCP server: the **Streamable HTTP** protocol, and the
name **`atlas-museum`** (add a version and a one-line description too).

Press **Check**: a real MCP client connects to `/mcp` and reads the server's name.
:::

:::step{type=task task=mcp_tools title="Your turn: offer the museum's tools" file="10-mcp/src/main/java/com/atlas/McpConfig.java" line="12"}
In `McpConfig.java`, add a `@Bean` method that offers the `@Tool` methods of `MuseumTools` as a `ToolCallbackProvider`.

Then talk to your server the way an MCP client does, in the next step. Press **Check**: the check's client lists your
tools and calls `openingHours`.
:::

:::step{type=try title="Speaking MCP by hand"}
MCP is plain HTTP and JSON, so curl can speak it. First, the client introduces itself with `initialize`:

```text
$ curl -s -D /tmp/h -X POST localhost:8080/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2025-06-18\",\"capabilities\":{},\"clientInfo\":{\"name\":\"curl\",\"version\":\"1\"}}}"; echo; grep -i mcp-session /tmp/h
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18","capabilities":{"completions":{},"logging":{},"prompts":{"listChanged":true},"resources":{"subscribe":false,"listChanged":true},"tools":{"listChanged":true}},"serverInfo":{"name":"atlas-museum","version":"1.0.0"},"instructions":"Facts about the Deccan Science Museum in Pune: dates, opening hours and planetarium shows."}}
Mcp-Session-Id: 0242b6b2-c1f2-4ae8-807c-e8863520a4e9
```

The server answers with its capabilities, its name and instructions, and a **session id** in a header, which the client
sends with every later message. (A client also sends a short `notifications/initialized` message next; the server
answers `202`.) Then it asks for the tools. Answers come as server-sent events, so `sed` keeps only the `data:` line:

```text
$ curl -s -X POST localhost:8080/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -H "Mcp-Session-Id: 0242b6b2-c1f2-4ae8-807c-e8863520a4e9" -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | sed -n 's/^data://p' | jq -c '.result.tools[] | {name, description}'
{"name":"today","description":"Today's date, as YYYY-MM-DD, and its day of the week."}
{"name":"openingHours","description":"The museum's opening hours on one date. The museum is closed on Mondays."}
{"name":"planetariumShows","description":"The planetarium shows on one date, with their start times and free seats."}
{"name":"nextDay","description":"The date of the next given day of the week, counting today. Use it for 'this Saturday' or 'next Monday'."}
```

Your four tools, with the descriptions you wrote in chapter 7. And a call, exactly what an assistant's model would ask
for:

```text
$ curl -s -X POST localhost:8080/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -H "Mcp-Session-Id: 0242b6b2-c1f2-4ae8-807c-e8863520a4e9" -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"planetariumShows","arguments":{"date":"2026-11-28"}}}' | sed -n 's/^data://p' | jq -c .result
{"content":[{"type":"text","text":"[{\"time\":\"11:00\",\"title\":\"Journey to the Moon\",\"freeSeats\":4},{\"time\":\"14:00\",\"title\":\"The Life of Stars\",\"freeSeats\":0},{\"time\":\"16:00\",\"title\":\"Black Holes\",\"freeSeats\":11}]"}],"isError":false}
```

Saturday's shows, from your Java code, through a standard any assistant understands. (Your session id will differ.)
:::

:::step{type=predict title="Guess first"}
:::question
The education office's assistant is written in Python and uses a different model. Can it use Atlas's MCP tools?
:::
- [ ] No: the tools are written in Java with Spring AI
- [x] Yes: MCP is a protocol; any MCP client can list and call the tools, whatever language and model it uses
- [ ] Only if it uses OpenAI too
:::explain
That is the whole point of a protocol: the server describes its tools in JSON and runs them; the client's model only
needs to know how to call tools, which almost all current models do.
:::
:::

:::step{type=concept title="The other side: Spring AI as an MCP client"}
Atlas can also **use** other people's MCP servers. The client starter (`spring-ai-starter-mcp-client`) connects to the
servers you list in properties, for example:

```properties
spring.ai.mcp.client.streamable-http.connections.weather.url=https://weather.example.com
```

and offers their tools to your `ChatClient` as a `ToolCallbackProvider`, alongside your own `@Tool` methods:

```java
chat.prompt().user(q).toolCallbacks(mcpTools).call().content();
```

So the same question ("Will it rain on Saturday, and are there seats for the planetarium?") could use a weather
service's MCP tool and your own booking tool in one answer. Remember chapter 8: tools from servers you do not control
can do anything their descriptions claim. Confirm the ones that change things
(`spring.ai.tools.confirmation.tools=...` works for MCP tools too), and only connect to servers you trust.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `spring.ai.mcp.server.protocol=STREAMABLE` give you?
:::
- [ ] A faster model
- [x] An MCP server over Streamable HTTP, at the /mcp endpoint
- [ ] Streaming answers from the model, as in chapter 4
:::explain
It chooses the MCP transport: Streamable HTTP, served by your Spring MVC app. It has nothing to do with streaming model
answers.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You add a new `@Tool` method to `MuseumTools`. What do MCP clients need to change to use it?
:::
- [x] Nothing: they discover tools with tools/list when they connect
- [ ] Their code, to add the new tool
- [ ] Their model, which must be retrained
:::explain
Discovery is built into the protocol. Servers can even notify connected clients that the tool list changed (the
`listChanged` capability you saw in the initialize answer).
:::
:::

:::step{type=deep-dive title="Go deeper: annotations, resources, security"}
**MCP annotations.** Spring AI also has MCP-specific annotations (`@McpTool`, `@McpResource`, `@McpPrompt`) for servers
that want MCP features beyond plain tools, such as progress notifications or asking the user for input mid-call.

**Resources and prompts.** Atlas could offer its exhibit cards as **resources** (a client reads them as documents) and a
"plan a school visit" **prompt** template. Clients show prompts to users as ready-made commands.

**Stateless servers.** A stateless Streamable HTTP server keeps no session, so it scales behind a load balancer like any
REST API; Spring AI has a starter mode for it.

**Security.** An MCP server is an API that models call on someone's behalf: protect it like one. Use HTTPS and OAuth2
for remote servers (Spring AI's MCP security support builds on Spring Security), give each client the fewest tools it
needs, and remember that a tool's description is read by a model: never put instructions there that you would not want a
model to follow.
:::

:::step{type=recap}
You can now:

- explain what MCP is and why it exists: one protocol between AI applications and tools, M plus N instead of M times N;
- name the roles (server, client), the capabilities (tools, resources, prompts) and the transports (stdio, Streamable HTTP);
- turn a Spring Boot app into an MCP server with the starter, two properties and a `ToolCallbackProvider` bean;
- speak MCP by hand with curl (initialize, tools/list, tools/call), and connect Spring AI to other MCP servers as a client.

That ends Part 2. Next, Part 3: knowledge. Chapter 11 starts with embeddings, the idea behind teaching Atlas the museum's
own exhibits.

:::photo{src="/lesson-images/spring-ai/springai-10-notes.webp" alt="Handwritten notes about MCP: one protocol for tools; server offers, client uses; protocol=STREAMABLE, /mcp; ToolCallbackProvider bean; initialize, tools/list, tools/call" ai="true"}
One page of notes for this chapter.
:::
:::
