package com.setu;

import java.util.List;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.listener.ChatModelListener;
import dev.langchain4j.model.openai.OpenAiChatModel;

/** The chat model behind the LabBox gateway. */
public final class Models {

    private Models() {
    }

    public static ChatModel chatModel(String baseUrl, String apiKey, ChatModelListener... listeners) {
        return OpenAiChatModel.builder()
                .baseUrl(baseUrl)
                .apiKey(apiKey)
                .modelName("ai-chat")
                .temperature(0.0)
                .listeners(List.of(listeners))
                .build();
    }
}
