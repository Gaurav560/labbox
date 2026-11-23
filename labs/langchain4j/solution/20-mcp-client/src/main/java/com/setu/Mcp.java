package com.setu;

import java.nio.file.Path;
import java.util.List;

import dev.langchain4j.mcp.McpToolProvider;
import dev.langchain4j.mcp.client.DefaultMcpClient;
import dev.langchain4j.mcp.client.McpClient;
import dev.langchain4j.mcp.client.transport.McpTransport;
import dev.langchain4j.mcp.client.transport.stdio.StdioMcpTransport;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.service.AiServices;

/** Setu reads the railway's notices through an MCP server it did not write. */
public final class Mcp {

    private Mcp() {
    }

    /** The server runs as a child process; requests and answers travel over its standard input and output. */
    public static McpClient filesystem(Path folder) {
        McpTransport transport = StdioMcpTransport.builder()
                .command(List.of("mcp-server-filesystem", folder.toString()))
                .build();
        return DefaultMcpClient.builder()
                .key("notices")
                .transport(transport)
                .build();
    }

    /** Every tool the server offers (14 of them, including write_file and move_file) becomes Setu's tool. */
    public static Assistant assistantWithAllTools(ChatModel model, McpClient client) {
        return AiServices.builder(Assistant.class)
                .chatModel(model)
                .toolProvider(McpToolProvider.builder().mcpClients(client).build())
                .build();
    }

    /** Only the two reading tools: no writing, moving or searching by file name. */
    public static Assistant assistant(ChatModel model, McpClient client) {
        return AiServices.builder(Assistant.class)
                .chatModel(model)
                .toolProvider(McpToolProvider.builder()
                        .mcpClients(client)
                        .filterToolNames("list_directory", "read_text_file")
                        .build())
                .build();
    }
}
