package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;

/** Where Setu gets its chat model. */
public final class Models {

    private Models() {
    }

    /** An OpenAI chat model behind the LabBox gateway, as LangChain4j's ChatModel interface. */
    public static ChatModel chatModel(String baseUrl, String apiKey) {
        return OpenAiChatModel.builder()
                .baseUrl(baseUrl)
                .apiKey(apiKey)
                .modelName("ai-chat")
                .build();
    }
}
