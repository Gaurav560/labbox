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

    // TODO (task steady_model): build the model like chapter 9 (baseUrl, apiKey, "ai-chat"), and also give it
    //   temperature 0.0, so facts come out the same way every time.
    public static ChatModel steadyModel(String baseUrl, String apiKey) {
        return OpenAiChatModel.builder()
                .baseUrl(baseUrl)
                .apiKey(apiKey)
                .modelName("ai-chat")
                .build();
    }

    // TODO (task short_answer): send SYSTEM and the question in a ChatRequest that also sets maxOutputTokens(maxTokens),
    //   so this one answer can be at most that long. Return the whole ChatResponse.
    public static ChatResponse ask(ChatModel model, String question, int maxTokens) {
        return model.chat(SystemMessage.from(SYSTEM), UserMessage.from(question));
    }
}
