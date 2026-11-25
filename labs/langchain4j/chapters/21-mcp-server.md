:::step{type=story title="Setu's tools, for everyone"}
The fare and date tools from chapter 19 live inside Setu. Now other teams want them: the ticket office's new booking
app, a developer's coding assistant, the operations team's desktop AI app. Copying `RailTools` into each would be
chapter 20's problem again, from the other side.

So Sahyadri Rail will run its own **MCP server**: the same `RailTools` class, offered over MCP, so any MCP client can
start it and call `fare` and `nextDate`. In Java, with LangChain4j's community MCP server module, that is a dozen lines.

:::mission
Serve `RailTools` as a stdio MCP server, then connect to it from Java the way chapter 20 connected to the filesystem
server.
:::
:::

:::step{type=concept title="Your @Tool methods, served over MCP" file="21-mcp-server/src/main/java/com/setu/RailMcpServer.java" line="12-18"}
Two words first. Every program has a **standard input** (stdin), where it reads, and a **standard output** (stdout),
where `System.out.println` writes. A **stdio** server talks to its client through exactly these two streams: the
client writes requests into the server's stdin and reads answers from its stdout. The messages are **JSON-RPC**: one
JSON object per line, a request with an `id`, a `method` and `params`, and an answer with the same `id` and a
`result` or an `error`.

The module `langchain4j-community-mcp-server` turns `@Tool` methods into such a server. Its stdio form has four steps:

```java
McpImplementation info = new McpImplementation();   // who this server is
info.setName("sahyadri-rail");
info.setVersion("1.0.0");
McpServer server = new McpServer(List.of(new RailTools()), info);   // the tools to serve
new StdioMcpServerTransport(System.in, System.out, server);          // speak MCP on stdin/stdout
Thread.currentThread().join();                                        // keep running
```

The tools are exactly chapter 19's: the `@Tool` descriptions become the MCP tool descriptions, the `@P` descriptions
the parameter descriptions. One class now serves Setu's own AI Service **and** any outside client.

Two rules from LangChain4j's server guide matter:

1. **Nothing else may write to `System.out`.** Standard output **is** the protocol. The MCP specification says the
   server "MUST NOT write anything to its stdout that is not a valid MCP message", and the guide warns that the client
   will disconnect. Logs go to standard error (`System.err`), which the specification allows. This project's logger is
   silent (`slf4j-nop`).
2. **Parameter names come from the compiled code**, so compile with `-parameters` (Spring Boot's parent already
   does). We compiled `RailTools` without it on 26 November: the client saw the parameter as `arg0`, sent
   `{"destination": "Ratnagiri"}` anyway, and the server's `fare` got `null`:
   `Cannot invoke "String.trim()" because "<parameter1>" is null`.
:::

:::step{type=task task=mcp_server title="Your turn: the server" file="21-mcp-server/src/main/java/com/setu/RailMcpServer.java" line="12-18"}
Finish `RailMcpServer.main`, in this order:

1. create the `McpImplementation` and set its name `sahyadri-rail` and version `1.0.0`;
2. create an `McpServer` with `List.of(new RailTools())` and that info;
3. create a `StdioMcpServerTransport` on `System.in` and `System.out` with the server;
4. keep the process alive with `Thread.currentThread().join()`.

The usual slip: leaving out step 4. The transport reads on a background thread, so `main` returns, the process ends,
and the client never gets an answer. We tried it on 26 November: the client reported the same timeout you will meet
in a moment ("The server answered neither ... request nor the ... initialization").

Press **Check**.
:::

:::step{type=concept title="Connecting to your own server" file="21-mcp-server/src/main/java/com/setu/RailClient.java" line="16-21"}
A stdio server is just a program, so a client starts it with a command. For a Java server, the command is
`java -cp <classpath> com.setu.RailMcpServer`:

```java
StdioMcpTransport.builder()
        .command(List.of("java", "-cp", classpath, "com.setu.RailMcpServer"))
        .build();
```

The same shape goes into any MCP client's configuration, for example a desktop assistant's `.mcp.json`:

```json
{"mcpServers": {"sahyadri-rail": {"command": "java", "args": ["-jar", "/opt/setu/rail-mcp-server.jar"]}}}
```

(In production you would package the server as one runnable jar, so the command is `java -jar` with one path.)
:::

:::step{type=task task=own_server_client title="Your turn: the client" file="21-mcp-server/src/main/java/com/setu/RailClient.java" line="16-21"}
Finish `RailClient.connect(classpath)`: a `StdioMcpTransport` with the command
`List.of("java", "-cp", classpath, "com.setu.RailMcpServer")`, and a `DefaultMcpClient` with key `"sahyadri-rail"`
and that transport.

The usual slip: a typo in the class name, such as `com.setu.RailMcpServr`. Java cannot find the class, the server
process dies at once, and the client again reports a timeout (we tried it on 26 November).

```bash run
cd /workspace/21-mcp-server && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Careful: a timeout that was not a timeout"}
When we first wrote this chapter, `Setu.java` passed `System.getProperty("java.class.path")` as the classpath. It
failed like this:

```text
[ERROR] Failed to execute goal org.codehaus.mojo:exec-maven-plugin:3.7.0:java (default-cli) on project setu: An exception occurred while executing the Java class. java.util.concurrent.TimeoutException. The server answered neither the 2026-07-28 protocol detection request nor the 2025-11-25 initialization that followed it. If the server does not tolerate being sent a method it does not know, skip detection by setting the protocol version explicitly, for example .protocolVersion("2025-11-25"). -> [Help 1]
```

The message suggests a protocol problem, and pinning the protocol version changed nothing. The real cause was more
basic: `mvn exec:java` runs your program **inside Maven's own JVM**, where `java.class.path` is Maven's classpath, not
your project's. The server process was started, could not find `com.setu.RailMcpServer`, and died at once; the client
waited for an answer that never came. `Setu.classpath()` now takes the classpath from the class loader that really
loaded your classes.

We reproduced it on 26 November, word for word. Inside `mvn exec:java`, `java.class.path` was
`/opt/maven/boot/plexus-classworlds-2.8.0.jar`, Maven's own launcher. Running the server's command by hand with that
classpath showed the real problem in one second:

```text
$ java -cp /opt/maven/boot/plexus-classworlds-2.8.0.jar com.setu.RailMcpServer
Error: Could not find or load main class com.setu.RailMcpServer
Caused by: java.lang.ClassNotFoundException: com.setu.RailMcpServer
```

The lesson for every stdio server: when a client times out, **run the server's command yourself** first. A server
that cannot start always looks like a server that does not answer. In this chapter three different mistakes (a
wrong classpath, a typo in the class name, a missing `join()`) all gave the same timeout message.
:::

:::step{type=concept title="What travels between them"}
To see the real messages, we put `tee` (a command that copies a stream into a file as it passes) on both of the
server's streams while `Setu.java` ran (26 November). Each line is one JSON-RPC message; shortened here:

```text
client -> server  {"id":0,"method":"server/discover","params":{... "protocolVersion":"2026-07-28" ...}}
server -> client  {"id":0,"error":{"code":-32601,"message":"Method not found: server/discover"}}
client -> server  {"id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25", ...}}
server -> client  {"id":1,"result":{"protocolVersion":"2025-11-25","serverInfo":{"name":"sahyadri-rail","version":"1.0.0"}, ...}}
client -> server  {"method":"notifications/initialized"}
client -> server  {"id":3,"method":"tools/list"}
server -> client  {"id":3,"result":{"tools":[{"name":"fare", ...},{"name":"nextDate", ...}]}}
client -> server  {"id":4,"method":"tools/call","params":{"name":"fare","arguments":{"destination":"Ratnagiri"}}}
server -> client  {"id":4,"result":{"content":[{"type":"text","text":"420"}]}}
```

:::diagram{name="l4j-mcp-wire"}
The real messages of one run.
:::

Three things to notice:

- **The first request fails, on purpose.** LangChain4j 1.24's client first asks with the newest protocol version it
  knows (2026-07-28). This server does not know that method and says "Method not found" (error code -32601 is
  JSON-RPC's code for that). The client then falls back to `initialize` with version 2025-11-25, which the server
  accepts. That is why the timeout message names both versions.
- **Answers are matched by `id`**, not by order. The notification has no `id` because it needs no answer.
- **The tool list carries your annotations.** The `@Tool` text became `description`, and the `@P` text became the
  description of the `destination` parameter. That is all an outside client knows about your tool.
:::

:::step{type=try title="Your tools, over MCP"}
```text
$ mvn -q compile exec:java
fare: The fare in rupees for one adult ticket from Pune to a station. Children under 5 travel free.
nextDate: The date (YYYY-MM-DD) of the next given day of the week, after today
fare(Ratnagiri) over MCP = 420

> How much do two adults pay from Pune to Lonavala?
The fare for one adult ticket from Pune to Lonavala is ₹90. Therefore, two adults will pay ₹180 in total.
```

(We ran it again on 26 November: the same output, word for word.)

The client listed both tools with the descriptions from your annotations, called `fare("Ratnagiri")` directly over
MCP (no model involved: MCP tools are just remote functions), and then Setu, given the server's tools through
`McpToolProvider`, priced two tickets to Lonavala correctly. The model asked; a separate Java process answered.
:::

:::step{type=predict title="Guess first"}
:::question
We added `System.out.println("server started")` at the top of `RailMcpServer.main` and ran `Setu.java` (26
November). What happened?
:::
- [ ] The connection broke at once
- [x] It still worked: LangChain4j's client skipped the stray line, but the specification forbids it
- [ ] "server started" appeared in Setu's console
:::explain
The client listed both tools and got 420 for Ratnagiri; the line was dropped, not shown. That is luck, not a rule:
the MCP specification says a server must not write anything else to stdout, and LangChain4j's own guide warns that
the client will disconnect. Another client, or another version, may stop at that line. Log to standard error.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does an MCP client need to use a stdio server?
:::
- [x] The command that starts it
- [ ] Its source code
- [ ] A shared database
:::explain
The client starts the command and speaks MCP over its standard streams. That is why one `.mcp.json` line is enough to
add a server to an app.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why serve RailTools over MCP instead of copying the class into each app?
:::
- [ ] MCP is faster than a method call
- [x] One implementation, maintained once, usable by every MCP client in any language
- [ ] Copying classes is not allowed
:::explain
A fare change is made in one place, and every client, Java or not, gets it.
:::
:::

:::step{type=deep-dive title="Go deeper: servers for real"}
**HTTP servers.** A stdio server serves one client per process. For a shared service, use Streamable HTTP; the
community module does not offer it, and LangChain4j's server guide lists other Java projects that do: Helidon MCP,
the official MCP Java SDK (Spring AI's MCP support is built on it), Micronaut MCP, Quarkus MCP Server and Tachyon.
The guide notes they are not maintained by the LangChain4j team.

**Security.** A tool served over HTTP is an API on the network: authenticate clients, rate-limit, and never expose a
tool that changes data without checks inside it.

**Versioning.** Clients read your tool descriptions at run time, so renaming a tool or a parameter breaks them. Treat
tool names like a public API.

**Testing.** Test the tools as plain Java (as chapter 19's check does with a fixed clock), and test the server once
end to end, as this chapter's check does.
:::

:::step{type=recap}
You can now:

- serve `@Tool` methods as a stdio MCP server with `McpServer` and `StdioMcpServerTransport`;
- connect to your own server with a `java` command, from Java or from any MCP client's configuration;
- read the JSON-RPC messages a client and a server exchange;
- keep standard output clean on a stdio server, and debug a server that will not start;
- explain when to choose stdio and when Streamable HTTP.

Next, chapter 22: knowledge. Embedding models and embedding stores, the database half of retrieval.

:::photo{src="/lesson-images/langchain4j/l4j-21-notes.webp" alt="Handwritten notes titled Your own MCP server: McpServer serves your @Tool methods over standard input and output, one JSON message per line; the client starts the server, then initialize, tools/list, tools/call fare, answer 420; a wrong classpath, a typo or no join all give the same timeout; run the server command yourself to see the real error; without -parameters the client sees arg0; logs go to stderr, never stdout" ai="true"}
One page of notes for this chapter.
:::
:::
