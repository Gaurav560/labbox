package com.atlas;

import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** Shares Atlas's museum tools with any MCP client: other AI apps, desktop assistants, IDEs. */
@Configuration
public class McpConfig {

    // TODO (task mcp_tools): offer the methods of MuseumTools to MCP clients, as a ToolCallbackProvider bean.

}
