package com.setu;

import java.util.List;

import dev.langchain4j.community.mcp.server.McpServer;
import dev.langchain4j.community.mcp.server.transport.StdioMcpServerTransport;
import dev.langchain4j.mcp.protocol.McpImplementation;

/** Setu's rail tools as an MCP server: any MCP client (another app, an IDE, a desktop assistant) can use them. */
public class RailMcpServer {

    public static void main(String[] args) throws Exception {
        McpImplementation info = new McpImplementation();
        info.setName("sahyadri-rail");
        info.setVersion("1.0.0");
        McpServer server = new McpServer(List.of(new RailTools()), info);
        new StdioMcpServerTransport(System.in, System.out, server);
        Thread.currentThread().join();   // stdin stays open while the client is connected
    }
}
