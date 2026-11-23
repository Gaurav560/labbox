package com.setu;

/** Chapter 13: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        Assistant setu = Desk.assistant(Models.chatModel(System.getenv("OPENAI_BASE_URL"), System.getenv("OPENAI_API_KEY")));
        System.out.println(setu.getClass().getName());
        System.out.println(setu.chat("Hello! Who are you, and how can you help me?"));
    }
}
