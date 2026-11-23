package com.setu;

import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.service.AiServices;

/** Conversations that remember, one passenger or many. */
public final class Memories {

    private Memories() {
    }

    // TODO (task window_memory): build the Assistant with AiServices.builder(Assistant.class), the model, and a
    //   chatMemory(...) of MessageWindowChatMemory.withMaxMessages(10), so it remembers the last 10 messages.
    public static Assistant assistant(ChatModel model) {
        return AiServices.create(Assistant.class, model);
    }

    // TODO (task memory_per_passenger): build the PassengerDesk with AiServices.builder(PassengerDesk.class), the
    //   model, and a chatMemoryProvider(...) that gives each memory id its own MessageWindowChatMemory of 10 messages:
    //   id -> MessageWindowChatMemory.builder().id(id).maxMessages(10).build()
    public static PassengerDesk desk(ChatModel model) {
        return AiServices.create(PassengerDesk.class, model);
    }
}
