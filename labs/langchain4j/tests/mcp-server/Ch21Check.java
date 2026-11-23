package com.setu.check;

import java.time.Duration;
import java.util.List;

import org.junit.jupiter.api.Test;

import com.setu.RailClient;

import dev.langchain4j.agent.tool.ToolExecutionRequest;
import dev.langchain4j.mcp.client.DefaultMcpClient;
import dev.langchain4j.mcp.client.McpClient;
import dev.langchain4j.mcp.client.transport.stdio.StdioMcpTransport;

class Ch21Check {

    static final String CP = System.getProperty("java.class.path");

    @Test
    void mcpServer() {
        R.task("mcp_server", () -> {
            McpClient client;
            try {
                client = DefaultMcpClient.builder().key("check")
                        .initializationTimeout(Duration.ofSeconds(20))
                        .transport(StdioMcpTransport.builder().command(List.of("java", "-cp", CP, "com.setu.RailMcpServer")).build())
                        .build();
            } catch (RuntimeException e) {
                R.fail("mcp_server", "Started RailMcpServer, but it never answered as an MCP server. Its main must create an McpServer with List.of(new RailTools()) and serve it with new StdioMcpServerTransport(System.in, System.out, server), then keep running (Thread.currentThread().join()).");
                return;
            }
            try (client) {
                List<String> names = client.listTools().stream().map(t -> t.name()).toList();
                if (!names.contains("fare") || !names.contains("nextDate")) {
                    R.fail("mcp_server", "The server answers, but offers " + names + ": pass new RailTools() to the McpServer.", "[fare, nextDate]", names.toString());
                    return;
                }
                String fare = client.executeTool(ToolExecutionRequest.builder().id("1").name("fare").arguments("{\"destination\": \"Ratnagiri\"}").build()).resultText();
                if (!"420".equals(fare.strip())) {
                    R.fail("mcp_server", "fare(Ratnagiri) over MCP should be 420.", "420", fare);
                    return;
                }
            }
            R.pass("mcp_server", "Your Java tools, served over MCP: any MCP client can now ask Sahyadri Rail for fares and dates.");
        });
    }

    @Test
    void ownServerClient() {
        R.task("own_server_client", () -> {
            McpClient client;
            try {
                client = RailClient.connect(CP);
            } catch (RuntimeException e) {
                R.fail("own_server_client", "RailClient.connect could not reach the server: " + String.valueOf(e.getMessage()).lines().findFirst().orElse("") + ". Make the server task pass first; then check the command: java, -cp, the classpath, com.setu.RailMcpServer.");
                return;
            }
            if (client == null) {
                R.fail("own_server_client", "RailClient.connect returned null. Build a StdioMcpTransport with the java command, then a DefaultMcpClient with key \"sahyadri-rail\" and that transport.");
                return;
            }
            try (client) {
                List<String> names = client.listTools().stream().map(t -> t.name()).toList();
                if (!names.contains("fare")) {
                    R.fail("own_server_client", "Connected, but the tools are " + names + ".", "[fare, nextDate]", names.toString());
                    return;
                }
            }
            R.pass("own_server_client", "Client and server, both yours: the same protocol Claude Desktop, IDEs and agents use.");
        });
    }
}
