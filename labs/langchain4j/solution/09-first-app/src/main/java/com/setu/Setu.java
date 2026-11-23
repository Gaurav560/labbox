package com.setu;

import dev.langchain4j.model.chat.ChatModel;

/** Chapter 9: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        ChatModel model = Models.chatModel(System.getenv("OPENAI_BASE_URL"), System.getenv("OPENAI_API_KEY"));
        String question = "Hello! Who are you?";
        System.out.println("Without instructions: " + model.chat(question));
        System.out.println("As Setu:              " + Desk.ask(model, question));
    }
}
