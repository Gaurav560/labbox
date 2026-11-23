package com.setu;

import java.util.List;

import dev.langchain4j.mcp.client.DefaultMcpClient;
import dev.langchain4j.mcp.client.McpClient;
import dev.langchain4j.mcp.client.transport.McpTransport;
import dev.langchain4j.mcp.client.transport.stdio.StdioMcpTransport;

/** Connects to your own server, exactly as chapter 20 connected to someone else's. */
public final class RailClient {

    private RailClient() {
    }

    /** Your server, started as a child process by the client. */
    public static McpClient connect(String classpath) {
        McpTransport transport = StdioMcpTransport.builder()
                .command(List.of("java", "-cp", classpath, "com.setu.RailMcpServer"))
                .build();
        return DefaultMcpClient.builder()
                .key("sahyadri-rail")
                .transport(transport)
                .build();
    }
}
