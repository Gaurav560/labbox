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
The module `langchain4j-community-mcp-server` turns `@Tool` methods into an MCP server. Its stdio form has four steps:

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

Two rules from the documentation matter:

1. **Nothing else may write to `System.out`.** Standard output **is** the protocol: one stray log line breaks the
   JSON-RPC stream and the client disconnects. This project's logger is silent (`slf4j-nop`); a real server logs to
   `System.err`.
2. **Parameter names come from the compiled code**, so compile with `-parameters` (Spring Boot's parent already
   does), or clients see `arg0` instead of `destination`.
:::

:::step{type=task task=mcp_server title="Your turn: the server" file="21-mcp-server/src/main/java/com/setu/RailMcpServer.java" line="12-18"}
Finish `RailMcpServer.main`: create the `McpImplementation` (name `sahyadri-rail`, version `1.0.0`), an `McpServer` with
`List.of(new RailTools())`, a `StdioMcpServerTransport` on `System.in` and `System.out`, and keep the process alive
with `Thread.currentThread().join()`.

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

The lesson for every stdio server: when a client times out, **run the server's command yourself** first. A server
that cannot start always looks like a server that does not answer.
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

The client listed both tools with the descriptions from your annotations, called `fare("Ratnagiri")` directly over
MCP (no model involved: MCP tools are just remote functions), and then Setu, given the server's tools through
`McpToolProvider`, priced two tickets to Lonavala correctly. The model asked; a separate Java process answered.
:::

:::step{type=predict title="Guess first"}
:::question
You add `log.info("server started")` with a logger that writes to standard output, in `RailMcpServer.main`. What
happens?
:::
- [ ] Nothing: logs are separate from the protocol
- [x] The client receives a line that is not JSON-RPC and the connection breaks
- [ ] The log appears in the client's console
:::explain
For a stdio server, standard output is the wire. Log to standard error, or to a file.
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
documentation lists Java options: Quarkus MCP Server, Micronaut MCP, Helidon MCP, and the official MCP Java SDK
(Spring AI's MCP support is built on it).

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
- keep standard output clean on a stdio server, and debug a server that will not start;
- explain when to choose stdio and when Streamable HTTP.

Next, chapter 22: knowledge. Embedding models and embedding stores, the database half of retrieval.

:::photo{src="/lesson-images/langchain4j/l4j-21-notes.webp" alt="Handwritten notes about an MCP server: your @Tool methods as a server; McpServer plus a stdio transport; stdout is the wire, so no logs there; a client starts it with a command; on a timeout, run the command yourself" ai="true"}
One page of notes for this chapter.
:::
:::
