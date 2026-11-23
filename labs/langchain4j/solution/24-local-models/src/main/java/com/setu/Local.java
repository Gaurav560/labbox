package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.router.ChatModelRoutingResult;
import dev.langchain4j.model.chat.router.RoutingChatModel;
import dev.langchain4j.model.ollama.OllamaChatModel;

/** A model on your own machine, and a model that sends each request to the right model. */
public final class Local {

    private Local() {
    }

    /** An open model served by Ollama on your own machine: no key, no per-token bill. */
    public static ChatModel ollama(String baseUrl, String modelName) {
        return OllamaChatModel.builder()
                .baseUrl(baseUrl)
                .modelName(modelName)
                .temperature(0.0)
                .build();
    }

    /** Short messages to the small model, long ones to the large one: still just a ChatModel. */
    public static ChatModel routing(ChatModel small, ChatModel large) {
        return RoutingChatModel.builder()
                .route("simple", "greetings and short questions", small)
                .route("complex", "long questions and complaints", large)
                .router(request -> ChatModelRoutingResult.route(lastLength(request.chatRequest()) > 120 ? "complex" : "simple"))
                .defaultRoute("complex")
                .build();
    }

    /** How long the passenger's last message is, in characters. */
    static int lastLength(dev.langchain4j.model.chat.request.ChatRequest request) {
        var messages = request.messages();
        var last = messages.get(messages.size() - 1);
        return last instanceof dev.langchain4j.data.message.UserMessage u ? u.singleText().length() : 0;
    }
}
