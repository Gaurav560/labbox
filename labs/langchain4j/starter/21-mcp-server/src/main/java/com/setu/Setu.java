package com.setu;

import java.util.Map;

import dev.langchain4j.agent.tool.ToolExecutionRequest;
import dev.langchain4j.mcp.client.McpClient;
import dev.langchain4j.mcp.McpToolProvider;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.service.AiServices;

/** Chapter 21: run with  mvn -q compile exec:java */
public class Setu {

    /** This program's classpath, so the server can be started with the same classes (Maven's exec:java runs us
     *  inside Maven, where the java.class.path property is Maven's own). */
    static String classpath() {
        if (Thread.currentThread().getContextClassLoader() instanceof java.net.URLClassLoader loader) {
            StringBuilder cp = new StringBuilder();
            for (java.net.URL url : loader.getURLs()) {
                cp.append(cp.isEmpty() ? "" : java.io.File.pathSeparator).append(url.getPath());
            }
            return cp.toString();
        }
        return System.getProperty("java.class.path");
    }

    public static void main(String[] args) throws Exception {
        String classpath = classpath();
        try (McpClient rail = RailClient.connect(classpath)) {
            rail.listTools().forEach(t -> System.out.println(t.name() + ": " + t.description()));
            String fare = rail.executeTool(ToolExecutionRequest.builder().id("1").name("fare")
                    .arguments("{\"destination\": \"Ratnagiri\"}").build()).resultText();
            System.out.println("fare(Ratnagiri) over MCP = " + fare);

            ChatModel model = OpenAiChatModel.builder().baseUrl(System.getenv("OPENAI_BASE_URL"))
                    .apiKey(System.getenv("OPENAI_API_KEY")).modelName("ai-chat").temperature(0.0).build();
            Assistant setu = AiServices.builder(Assistant.class).chatModel(model)
                    .toolProvider(McpToolProvider.builder().mcpClients(rail).build()).build();
            System.out.println("\n> How much do two adults pay from Pune to Lonavala?");
            System.out.println(setu.chat("How much do two adults pay from Pune to Lonavala?"));
        }
    }
}
