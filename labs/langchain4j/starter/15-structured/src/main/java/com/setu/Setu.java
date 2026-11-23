package com.setu;

import dev.langchain4j.service.AiServices;

/** Chapter 15: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        Reader reader = AiServices.create(Reader.class, Models.structuredModel(System.getenv("OPENAI_BASE_URL"),
                System.getenv("OPENAI_API_KEY")));
        System.out.println(reader.trip("Hi, I need 3 tickets from Pune to Karjat this coming Saturday morning please"));
    }
}
