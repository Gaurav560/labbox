package com.setu;

import dev.langchain4j.model.chat.ChatModel;

/** Chapter 27: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        ChatModel model = Models.chatModel(System.getenv("OPENAI_BASE_URL"), System.getenv("OPENAI_API_KEY"));
        System.out.println("classifier alone: " + Agents.classifier(model).classify("I cancelled yesterday, where is my money?"));
        DeskWorkflow desk = Agents.desk(model);
        for (String m : new String[] {"I cancelled yesterday, where is my money?",
                "The 7:15 was 40 minutes late again and nobody announced anything!"}) {
            System.out.println("\n> " + m + "\n" + desk.handle(m));
        }
    }
}
