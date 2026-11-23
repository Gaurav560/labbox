package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;

/** Where Setu gets its chat model. */
public final class Models {

    private Models() {
    }

    // TODO (task chat_model): build an OpenAiChatModel with OpenAiChatModel.builder(): the baseUrl, the apiKey,
    //   and the model name "ai-chat" (the alias the LabBox gateway gives this course).
    public static ChatModel chatModel(String baseUrl, String apiKey) {
        return null;
    }
}
