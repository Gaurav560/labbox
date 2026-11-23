package com.setu;

import com.openai.client.OpenAIClient;

/** Chapter 8: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        OpenAIClient client = Sdk.client(System.getenv("OPENAI_BASE_URL"), System.getenv("OPENAI_API_KEY"));
        System.out.println(Sdk.ask(client, "Hello! Which trains do you run?"));
    }
}
