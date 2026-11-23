package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.service.AiServices;

/** Setu with tools: it can ask Java for fares and dates instead of guessing. */
public final class Desk {

    private Desk() {
    }

    // TODO (task tools_in_service): build the Assistant with AiServices.builder(Assistant.class), the model,
    //   and .tools(tools), so the model can call RailTools' @Tool methods.
    public static Assistant assistant(ChatModel model, RailTools tools) {
        return AiServices.create(Assistant.class, model);
    }
}
