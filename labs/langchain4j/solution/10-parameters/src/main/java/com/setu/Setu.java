package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.openai.OpenAiChatModel;

/** Chapter 10: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        String baseUrl = System.getenv("OPENAI_BASE_URL");
        String apiKey = System.getenv("OPENAI_API_KEY");
        String slogan = "Write a slogan for Sahyadri Rail's monsoon trains, in at most eight words.";

        ChatModel playful = OpenAiChatModel.builder().baseUrl(baseUrl).apiKey(apiKey).modelName("ai-chat")
                .temperature(1.5).build();
        ChatModel steady = Tuned.steadyModel(baseUrl, apiKey);
        for (int i = 1; i <= 3; i++) {
            System.out.println("temperature 1.5, try " + i + ": " + playful.chat(slogan));
        }
        for (int i = 1; i <= 3; i++) {
            System.out.println("temperature 0.0, try " + i + ": " + steady.chat(slogan));
        }

        ChatResponse cut = Tuned.ask(steady, "Describe the journey from Pune to Ratnagiri.", 20);
        System.out.println("\nmax 20 tokens: " + cut.aiMessage().text());
        System.out.println("finish reason: " + cut.finishReason());
    }
}
