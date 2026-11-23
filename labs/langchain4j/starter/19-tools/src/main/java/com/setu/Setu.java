package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;

/** Chapter 19: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        ChatModel model = OpenAiChatModel.builder().baseUrl(System.getenv("OPENAI_BASE_URL"))
                .apiKey(System.getenv("OPENAI_API_KEY")).modelName("ai-chat").temperature(0.0)
                .logRequests(false).build();
        Assistant setu = Desk.assistant(model, new RailTools());
        String q = "Today is Monday. I want 3 tickets from Pune to Karjat this coming Saturday. "
                + "What is the date, and how much will it cost?";
        System.out.println("> " + q);
        System.out.println(setu.chat(q));
        System.out.println("\n> How much is a ticket from Pune to Mumbai?");
        System.out.println(setu.chat("How much is a ticket from Pune to Mumbai?"));
    }
}
