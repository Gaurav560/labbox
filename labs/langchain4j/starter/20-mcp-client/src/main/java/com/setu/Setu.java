package com.setu;

import java.nio.file.Path;

import dev.langchain4j.mcp.client.McpClient;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;

/** Chapter 20: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) throws Exception {
        Path notices = Path.of("notices").toAbsolutePath();
        try (McpClient files = Mcp.filesystem(notices)) {
            System.out.println("The server offers " + files.listTools().size() + " tools:");
            files.listTools().forEach(t -> System.out.println("  " + t.name()));
            ChatModel model = OpenAiChatModel.builder().baseUrl(System.getenv("OPENAI_BASE_URL"))
                    .apiKey(System.getenv("OPENAI_API_KEY")).modelName("ai-chat").temperature(0.0).build();
            String q = "The notices are in " + notices + ". Is any work planned that affects the Konkan Breeze?";
            System.out.println("\n> " + q);
            System.out.println("all 14 tools: " + Mcp.assistantWithAllTools(model, files).chat(q));
            System.out.println("two tools:    " + Mcp.assistant(model, files).chat(q));
        }
    }
}
