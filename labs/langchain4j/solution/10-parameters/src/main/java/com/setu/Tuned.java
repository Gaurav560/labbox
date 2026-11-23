package com.setu;

import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.request.ChatRequest;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.openai.OpenAiChatModel;

/** The knobs: how creative the model is, and how long its answers may be. */
public final class Tuned {

    static final String SYSTEM = "You are Setu, the help desk assistant of Sahyadri Rail, a small hill railway between Pune, Lonavala, Karjat and Ratnagiri. Answer passengers in at most three short sentences.";

    private Tuned() {
    }

    /** A model with temperature 0: the most likely token every time. */
    public static ChatModel steadyModel(String baseUrl, String apiKey) {
        return OpenAiChatModel.builder()
                .baseUrl(baseUrl)
                .apiKey(apiKey)
                .modelName("ai-chat")
                .temperature(0.0)
                .build();
    }

    /** One request with its own limit on the answer's length. */
    public static ChatResponse ask(ChatModel model, String question, int maxTokens) {
        ChatRequest request = ChatRequest.builder()
                .messages(SystemMessage.from(SYSTEM), UserMessage.from(question))
                .maxOutputTokens(maxTokens)
                .build();
        return model.chat(request);
    }
}
