package com.setu;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;

/** A model that makes up an answer is worse than no answer. Two defences: permission to say "I don't know", and facts. */
public final class Honest {

    static final String SYSTEM = "You are Setu, the help desk assistant of Sahyadri Rail, a small hill railway between Pune, Lonavala, Karjat and Ratnagiri. Answer passengers in at most three short sentences.";

    private Honest() {
    }

    /** Setu's instructions, with permission (and an order) to say it does not know. */
    public static String honestSystem() {
        return SYSTEM + " If the answer is not in the facts you were given, say \"I don't know\" and suggest the station"
                + " office. Never invent times, fares or rules.";
    }

    /** The railway's real timetable and fares, from timetable.txt. */
    public static String facts() throws IOException {
        return Files.readString(Path.of("timetable.txt"));
    }

    /** The question, answered from the railway's own facts. */
    public static String ask(ChatModel model, String question) throws IOException {
        SystemMessage system = SystemMessage.from(honestSystem() + "\n\nFacts:\n" + facts());
        return model.chat(system, UserMessage.from(question)).aiMessage().text();
    }
}
