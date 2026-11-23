package com.setu;

/** Chapter 7: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) throws Exception {
        String baseUrl = System.getenv("OPENAI_BASE_URL");   // the LabBox gateway, set in your lab machine
        String apiKey = System.getenv("OPENAI_API_KEY");     // a key that only works at the gateway
        String question = "Hello! Which trains do you run?";

        System.out.println("== Request body\n" + Http.body(question));
        String response = Http.send(baseUrl, apiKey, question);
        System.out.println("\n== Response body\n" + response);
        System.out.println("\n== The answer\n" + Http.answer(response));
    }
}
