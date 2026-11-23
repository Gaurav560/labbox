package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.service.AiServices;

/** Chapter 14: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        ChatModel model = Models.chatModel(System.getenv("OPENAI_BASE_URL"), System.getenv("OPENAI_API_KEY"));
        String prompt = Announcements.delayPrompt("Konkan Breeze", "Ratnagiri", 25);
        System.out.println("PROMPT: " + prompt);
        System.out.println(model.chat(prompt));

        StationDesk desk = AiServices.create(StationDesk.class, model);
        for (String station : new String[] {"Lonavala", "Ratnagiri"}) {
            System.out.println("\nAt " + station + ": " + desk.ask(station, "How do I get from the station to the town centre?"));
        }
    }
}
