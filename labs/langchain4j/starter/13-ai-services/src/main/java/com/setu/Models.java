package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;

/** The chat model behind the LabBox gateway (chapter 9). */
public final class Models {

    private Models() {
    }

    public static ChatModel chatModel(String baseUrl, String apiKey) {
        return OpenAiChatModel.builder()
                .baseUrl(baseUrl)
                .apiKey(apiKey)
                .modelName("ai-chat")
                .temperature(0.0)
                .build();
    }
}
