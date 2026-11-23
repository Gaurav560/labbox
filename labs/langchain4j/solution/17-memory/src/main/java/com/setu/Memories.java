package com.setu;

import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.service.AiServices;

/** Conversations that remember, one passenger or many. */
public final class Memories {

    private Memories() {
    }

    /** One shared memory: fine for one user at a time, like a command-line chat. */
    public static Assistant assistant(ChatModel model) {
        return AiServices.builder(Assistant.class)
                .chatModel(model)
                .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
                .build();
    }

    /** A memory per passenger, made on first use and found again by its id. */
    public static PassengerDesk desk(ChatModel model) {
        return AiServices.builder(PassengerDesk.class)
                .chatModel(model)
                .chatMemoryProvider(id -> MessageWindowChatMemory.builder().id(id).maxMessages(10).build())
                .build();
    }
}
