package com.atlas.check;

import java.time.Duration;
import java.util.Map;
import java.util.stream.Collectors;

import io.modelcontextprotocol.client.McpClient;
import io.modelcontextprotocol.client.McpSyncClient;
import io.modelcontextprotocol.client.transport.HttpClientStreamableHttpTransport;
import io.modelcontextprotocol.spec.McpSchema;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;

/** Chapter 10: Atlas as an MCP server, tested with a real MCP client. */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class Ch10Check {
    static final FakeOpenAi AI = new FakeOpenAi();

    @DynamicPropertySource
    static void ai(DynamicPropertyRegistry r) {
        r.add("spring.ai.openai.base-url", AI::baseUrl);
        r.add("spring.ai.openai.api-key", () -> "check-key");
    }

    @AfterAll
    static void stop() {
        AI.stop();
    }

    @LocalServerPort
    int port;

    McpSyncClient client() {
        var transport = HttpClientStreamableHttpTransport.builder("http://127.0.0.1:" + port).endpoint("/mcp").build();
        return McpClient.sync(transport).requestTimeout(Duration.ofSeconds(10)).build();
    }

    @Test
    void mcpServer() {
        R.task("mcp_server", () -> {
            try (McpSyncClient c = client()) {
                McpSchema.InitializeResult init;
                try {
                    init = c.initialize();
                } catch (Exception e) {
                    R.fail("mcp_server", "no MCP server answered at /mcp. Set spring.ai.mcp.server.protocol=STREAMABLE in application.properties.");
                    return;
                }
                String name = init.serverInfo().name();
                if (!"atlas-museum".equals(name)) {
                    R.fail("mcp_server", "an MCP server answered, but with another name. Set spring.ai.mcp.server.name.", "atlas-museum", name);
                    return;
                }
                R.pass("mcp_server", "A real MCP client connected to /mcp and met atlas-museum: Atlas now speaks the protocol.");
            }
        });
    }

    @Test
    void mcpTools() {
        R.task("mcp_tools", () -> {
            try (McpSyncClient c = client()) {
                try {
                    c.initialize();
                } catch (Exception e) {
                    R.fail("mcp_tools", "no MCP server answered at /mcp yet: do the mcp_server task first.");
                    return;
                }
                var names = c.listTools().tools().stream().map(McpSchema.Tool::name).collect(Collectors.toList());
                if (!names.contains("openingHours") || !names.contains("planetariumShows")) {
                    R.fail("mcp_tools", "the server lists no museum tools yet. Return MethodToolCallbackProvider.builder().toolObjects(tools).build() from a @Bean method.", "openingHours, planetariumShows, ...", names.toString());
                    return;
                }
                McpSchema.CallToolResult r = c.callTool(new McpSchema.CallToolRequest("openingHours", Map.of("date", "2026-11-30")));
                String text = r.content().stream().filter(x -> x instanceof McpSchema.TextContent).map(x -> ((McpSchema.TextContent) x).text()).collect(Collectors.joining(" "));
                if (!text.toLowerCase().contains("closed")) {
                    R.fail("mcp_tools", "the client called openingHours for a Monday, but the answer did not say closed.", "Closed on 2026-11-30 ...", text);
                    return;
                }
                R.pass("mcp_tools", "An MCP client listed " + names.size() + " tools and called openingHours: any MCP-aware assistant can now use the museum's facts.");
            }
        });
    }
}
