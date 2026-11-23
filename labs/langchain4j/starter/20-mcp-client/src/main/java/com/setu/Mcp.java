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

    // TODO (task mcp_client): start the filesystem MCP server as a subprocess and connect to it.
    //   transport: StdioMcpTransport.builder().command(List.of("mcp-server-filesystem", folder.toString())).build()
    //   client:    DefaultMcpClient.builder().key("notices").transport(transport).build()
    public static McpClient filesystem(Path folder) {
        return null;
    }

    /** Every tool the server offers (14 of them, including write_file and move_file) becomes Setu's tool. */
    public static Assistant assistantWithAllTools(ChatModel model, McpClient client) {
        return AiServices.builder(Assistant.class)
                .chatModel(model)
                .toolProvider(McpToolProvider.builder().mcpClients(client).build())
                .build();
    }

    // TODO (task mcp_tool_provider): build the Assistant like assistantWithAllTools above, but give Setu only the two
    //   tools it needs to read notices: add .filterToolNames("list_directory", "read_text_file") to the
    //   McpToolProvider builder.
    public static Assistant assistant(ChatModel model, McpClient client) {
        return AiServices.create(Assistant.class, model);
    }
}
