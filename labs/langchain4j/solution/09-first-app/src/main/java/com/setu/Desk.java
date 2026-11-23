package com.setu;

import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;

/** Setu's help desk: every question goes to the model with Setu's instructions. */
public final class Desk {

    static final String SYSTEM = "You are Setu, the help desk assistant of Sahyadri Rail, a small hill railway between Pune, Lonavala, Karjat and Ratnagiri. Answer passengers in at most three short sentences.";

    private Desk() {
    }

    /** Setu's instructions first, then the passenger's question. */
    public static String ask(ChatModel model, String question) {
        ChatResponse response = model.chat(SystemMessage.from(SYSTEM), UserMessage.from(question));
        return response.aiMessage().text();
    }
}
