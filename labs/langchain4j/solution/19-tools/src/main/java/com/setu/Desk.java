package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.service.AiServices;

/** Setu with tools: it can ask Java for fares and dates instead of guessing. */
public final class Desk {

    private Desk() {
    }

    /** The model sees the tools' descriptions; LangChain4j runs a tool whenever the model asks for one. */
    public static Assistant assistant(ChatModel model, RailTools tools) {
        return AiServices.builder(Assistant.class)
                .chatModel(model)
                .tools(tools)
                .build();
    }
}
