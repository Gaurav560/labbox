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

    // TODO (task own_server_client): start your server with java and connect to it: a StdioMcpTransport whose
    //   command is List.of("java", "-cp", classpath, "com.setu.RailMcpServer"), and a DefaultMcpClient with
    //   key "sahyadri-rail" and that transport.
    public static McpClient connect(String classpath) {
        return null;
    }
}
