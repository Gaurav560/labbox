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

    // TODO (task honest_prompt): return SYSTEM plus one more instruction: if you do not know the answer from what you
    //   were given, say "I don't know" and suggest the station office; never invent times, fares or rules.
    //   Your text must contain the words "I don't know".
    public static String honestSystem() {
        return SYSTEM;
    }

    /** The railway's real timetable and fares, from timetable.txt. */
    public static String facts() throws IOException {
        return Files.readString(Path.of("timetable.txt"));
    }

    // TODO (task grounded_answer): ask with two messages: a SystemMessage with honestSystem() followed by a blank line,
    //   "Facts:" and facts(); then the UserMessage with the question. Return the answer's text.
    public static String ask(ChatModel model, String question) throws IOException {
        return model.chat(SystemMessage.from(SYSTEM), UserMessage.from(question)).aiMessage().text();
    }
}
