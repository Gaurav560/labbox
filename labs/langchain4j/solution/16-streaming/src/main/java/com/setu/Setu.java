package com.setu;

import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.service.AiServices;

/** Chapter 16: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) throws Exception {
        StreamingChatModel model = Streams.streamingModel(System.getenv("OPENAI_BASE_URL"), System.getenv("OPENAI_API_KEY"));
        long start = System.currentTimeMillis();
        long[] first = {0};
        int[] pieces = {0};
        Streams.stream(model, "In two sentences, why do trains slow down on a ghat?", token -> {
            if (first[0] == 0) {
                first[0] = System.currentTimeMillis();
            }
            pieces[0]++;
            System.out.print("[" + token + "]");
        }).get();
        long end = System.currentTimeMillis();
        System.out.println("\n" + pieces[0] + " pieces; first after " + (first[0] - start) + " ms, all after " + (end - start) + " ms");

        StreamingAssistant setu = AiServices.create(StreamingAssistant.class, model);
        String whole = Streams.ask(setu, "Hello! Which trains do you run?", System.out::print).get();
        System.out.println("\n(" + whole.length() + " characters)");
    }
}
