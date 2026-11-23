package com.setu;

import dev.langchain4j.model.chat.ChatModel;

/** Chapter 29: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        ChatModel model = Models.chatModel(System.getenv("OPENAI_BASE_URL"), System.getenv("OPENAI_API_KEY"), new Trace());
        String request = "We are 2 adults going from Pune to Ratnagiri next Sunday. What is the date, and the total fare?";
        System.out.println("> " + request);
        System.out.println(Supervisor.supervisor(model).invoke(request));
    }
}
