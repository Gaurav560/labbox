package com.atlas;

import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** Shares Atlas's museum tools with any MCP client: other AI apps, desktop assistants, IDEs. */
@Configuration
public class McpConfig {

    @Bean
    ToolCallbackProvider museumToolProvider(MuseumTools tools) {
        return MethodToolCallbackProvider.builder()
                .toolObjects(tools)
                .build();
    }

}
