package com.setu;

import dev.langchain4j.model.chat.ChatModel;

/** Chapter 17: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        ChatModel model = Models.chatModel(System.getenv("OPENAI_BASE_URL"), System.getenv("OPENAI_API_KEY"));
        Assistant setu = Memories.assistant(model);
        System.out.println("> My name is Meera and I am travelling to Karjat with my grandmother.");
        System.out.println(setu.chat("My name is Meera and I am travelling to Karjat with my grandmother."));
        System.out.println("> What is my name, and where am I going?");
        System.out.println(setu.chat("What is my name, and where am I going?"));

        PassengerDesk desk = Memories.desk(model);
        desk.chat("ravi", "Hi, I am Ravi. I lost my umbrella on the Monsoon Mail.");
        desk.chat("asha", "Hi, I am Asha. I want to book two seats to Ratnagiri.");
        System.out.println("\n> (ravi) What did I lose?");
        System.out.println(desk.chat("ravi", "What did I lose?"));
        System.out.println("> (asha) What did I lose?");
        System.out.println(desk.chat("asha", "What did I lose?"));
    }
}
