package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.service.AiServices;

/** Where Setu's AI Service is made. */
public final class Desk {

    private Desk() {
    }

    // TODO (task ai_service): let LangChain4j implement the Assistant interface for this model,
    //   with AiServices.create(Assistant.class, model).
    public static Assistant assistant(ChatModel model) {
        return null;
    }
}
