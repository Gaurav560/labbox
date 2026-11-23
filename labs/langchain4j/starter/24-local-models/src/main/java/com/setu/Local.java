package com.setu;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.router.ChatModelRoutingResult;
import dev.langchain4j.model.chat.router.RoutingChatModel;
import dev.langchain4j.model.ollama.OllamaChatModel;

/** A model on your own machine, and a model that sends each request to the right model. */
public final class Local {

    private Local() {
    }

    // TODO (task ollama_model): build an OllamaChatModel with OllamaChatModel.builder(): baseUrl(baseUrl),
    //   modelName(modelName) and temperature(0.0).
    public static ChatModel ollama(String baseUrl, String modelName) {
        return null;
    }

    // TODO (task routing_model): build a RoutingChatModel with two routes and a rule:
    //   .route("simple", "greetings and short questions", small)
    //   .route("complex", "long questions and complaints", large)
    //   .router(request -> ChatModelRoutingResult.route(lastLength(request.chatRequest()) > 120 ? "complex" : "simple"))
    //   .defaultRoute("complex"), then build().
    public static ChatModel routing(ChatModel small, ChatModel large) {
        return large;
    }

    /** How long the passenger's last message is, in characters. */
    static int lastLength(dev.langchain4j.model.chat.request.ChatRequest request) {
        var messages = request.messages();
        var last = messages.get(messages.size() - 1);
        return last instanceof dev.langchain4j.data.message.UserMessage u ? u.singleText().length() : 0;
    }
}
