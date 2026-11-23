package com.setu.check;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Mcp;

import dev.langchain4j.mcp.client.McpClient;
import dev.langchain4j.model.openai.OpenAiChatModel;

class Ch20Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    static Path notices() throws Exception {
        Path dir = Files.createTempDirectory("notices");
        Files.writeString(dir.resolve("track-work.txt"), "Track work near Karjat on Sunday.");
        return dir;
    }

    @Test
    void mcpClient() {
        R.task("mcp_client", () -> {
            Path dir = notices();
            McpClient client = Mcp.filesystem(dir);
            if (client == null) {
                R.fail("mcp_client", "Mcp.filesystem returned null. Build a StdioMcpTransport with the command mcp-server-filesystem and the folder, then a DefaultMcpClient with that transport.");
                return;
            }
            try (client) {
                List<String> names = client.listTools().stream().map(t -> t.name()).toList();
                if (!names.contains("list_directory") || !names.contains("read_text_file")) {
                    R.fail("mcp_client", "The client connected, but not to the filesystem server: its tools are " + names + ".", "list_directory, read_text_file, ...", names.toString());
                    return;
                }
            }
            R.pass("mcp_client", "Your Java program started a Node.js server and talked to it over MCP: 14 tools, none written by you.");
        });
    }

    @Test
    void mcpToolProvider() {
        R.task("mcp_tool_provider", () -> {
            Path dir = notices();
            FAKE.reset();
            FAKE.script = body -> FAKE.chatRequests.size() == 1
                    ? FakeOpenAi.Reply.tool("list_directory", "{\"path\": \"" + dir + "\"}")
                    : FakeOpenAi.Reply.text("There is track work near Karjat on Sunday.");
            var model = OpenAiChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-chat").build();
            McpClient client = dev.langchain4j.mcp.client.DefaultMcpClient.builder().key("notices")
                    .transport(dev.langchain4j.mcp.client.transport.stdio.StdioMcpTransport.builder()
                            .command(List.of("mcp-server-filesystem", dir.toString())).build()).build();
            try (client) {
                String got;
                try {
                    got = Mcp.assistant(model, client).chat("Any notices?");
                } catch (RuntimeException e) {
                    R.fail("mcp_tool_provider", "The model asked for list_directory, but Setu has none of the server's tools, so LangChain4j stopped. Build the Assistant with a .toolProvider(McpToolProvider.builder().mcpClients(client).filterToolNames(...).build()).");
                    return;
                }
                List<String> tools = FakeOpenAi.tools(FAKE.chat(0));
                if (tools.isEmpty()) {
                    R.fail("mcp_tool_provider", "The model was offered no tools. Build the Assistant with a .toolProvider(McpToolProvider.builder().mcpClients(client)...build()).");
                    return;
                }
                if (!new java.util.TreeSet<>(tools).equals(new java.util.TreeSet<>(List.of("list_directory", "read_text_file")))) {
                    R.fail("mcp_tool_provider", "Setu was offered " + tools.size() + " tools, including ones that write and move files. Add .filterToolNames(\"list_directory\", \"read_text_file\") to the McpToolProvider builder.",
                            "[list_directory, read_text_file]", tools.toString());
                    return;
                }
                if (FAKE.chatRequests.size() < 2 || !FAKE.chatRequests.get(1).contains("track-work.txt")) {
                    R.fail("mcp_tool_provider", "The model asked to list the folder, but the server's answer never came back to it.");
                    return;
                }
                if (!"There is track work near Karjat on Sunday.".equals(got)) {
                    R.fail("mcp_tool_provider", "chat(...) should return the model's final answer.", "There is track work near Karjat on Sunday.", String.valueOf(got));
                    return;
                }
            }
            R.pass("mcp_tool_provider", "Two tools out of fourteen: enough to read notices, nothing that can write or delete.");
        });
    }
}
