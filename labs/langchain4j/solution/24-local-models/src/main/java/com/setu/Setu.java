package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;

/** Chapter 24: run with  mvn -q compile exec:java  (the Ollama part needs an Ollama server: OLLAMA_URL) */
public class Setu {

    public static void main(String[] args) {
        String ollamaUrl = System.getenv("OLLAMA_URL");
        if (ollamaUrl != null) {
            ChatModel local = Local.ollama(ollamaUrl, "qwen2.5:0.5b");
            System.out.println("Local model: " + local.chat("In one sentence: what is a hill railway?"));
        } else {
            System.out.println("No OLLAMA_URL: skipping the local model (no Ollama server in this lab).");
        }

        String url = System.getenv("OPENAI_BASE_URL");
        String key = System.getenv("OPENAI_API_KEY");
        ChatModel small = OpenAiChatModel.builder().baseUrl(url).apiKey(key).modelName("ai-chat").maxTokens(60).build();
        ChatModel large = OpenAiChatModel.builder().baseUrl(url).apiKey(key).modelName("ai-chat").maxTokens(400).build();
        ChatModel routed = Local.routing(small, large);
        for (String q : new String[] {"Hi!", "Last Sunday the Konkan Breeze stopped for two hours near Karjat in heavy rain, "
                + "nobody told us why, and we missed our connection to Ratnagiri. What should we have done, and can we get anything back?"}) {
            String a = routed.chat(q);
            System.out.println("\n> " + q + "\n(" + (q.length() > 120 ? "complex" : "simple") + " route) " + a);
        }
    }
}
