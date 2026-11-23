package com.setu;

import java.util.List;

import dev.langchain4j.community.mcp.server.McpServer;
import dev.langchain4j.community.mcp.server.transport.StdioMcpServerTransport;
import dev.langchain4j.mcp.protocol.McpImplementation;

/** Setu's rail tools as an MCP server: any MCP client (another app, an IDE, a desktop assistant) can use them. */
public class RailMcpServer {

    // TODO (task mcp_server): serve RailTools over MCP on standard input and output.
    //   1. McpImplementation info = new McpImplementation(); info.setName("sahyadri-rail"); info.setVersion("1.0.0");
    //   2. McpServer server = new McpServer(List.of(new RailTools()), info);
    //   3. new StdioMcpServerTransport(System.in, System.out, server);
    //   4. keep the process alive: Thread.currentThread().join();
    public static void main(String[] args) throws Exception {
    }
}
