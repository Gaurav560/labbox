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

    // TODO (task system_message): send two messages with model.chat(...): a SystemMessage with SYSTEM, then a
    //   UserMessage with the question. Return the text of the answer's AiMessage.
    public static String ask(ChatModel model, String question) {
        return model.chat(question);
    }
}
