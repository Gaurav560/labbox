package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.service.AiServices;

/** Where Setu's AI Service is made. */
public final class Desk {

    private Desk() {
    }

    /** A proxy that turns each call of chat(...) into a request to the model. */
    public static Assistant assistant(ChatModel model) {
        return AiServices.create(Assistant.class, model);
    }
}
