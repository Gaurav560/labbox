package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.service.AiServices;

/** Setu with a guard on the way in and a guard on the way out. */
public final class Desk {

    private Desk() {
    }

    public static Assistant assistant(ChatModel model) {
        return AiServices.builder(Assistant.class)
                .chatModel(model)
                .inputGuardrails(new QuestionLimit())
                .outputGuardrails(new NoPhoneNumbers())
                .build();
    }
}
