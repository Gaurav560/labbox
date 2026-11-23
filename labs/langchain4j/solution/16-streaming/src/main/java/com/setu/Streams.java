package com.setu;

import java.util.concurrent.CompletableFuture;
import java.util.function.Consumer;

import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.chat.response.StreamingChatResponseHandler;
import dev.langchain4j.model.openai.OpenAiStreamingChatModel;
import dev.langchain4j.service.TokenStream;

/** Answers that appear word by word, as the model writes them. */
public final class Streams {

    private Streams() {
    }

    public static StreamingChatModel streamingModel(String baseUrl, String apiKey) {
        return OpenAiStreamingChatModel.builder()
                .baseUrl(baseUrl)
                .apiKey(apiKey)
                .modelName("ai-chat")
                .build();
    }

    /** The low-level way: a handler with three callbacks. */
    public static CompletableFuture<ChatResponse> stream(StreamingChatModel model, String question, Consumer<String> onToken) {
        CompletableFuture<ChatResponse> done = new CompletableFuture<>();
        model.chat(question, new StreamingChatResponseHandler() {
            @Override
            public void onPartialResponse(String partialResponse) {
                onToken.accept(partialResponse);
            }

            @Override
            public void onCompleteResponse(ChatResponse completeResponse) {
                done.complete(completeResponse);
            }

            @Override
            public void onError(Throwable error) {
                done.completeExceptionally(error);
            }
        });
        return done;
    }

    /** The AI Service way: the method returns a TokenStream, and nothing happens until start(). */
    public static CompletableFuture<String> ask(StreamingAssistant setu, String question, Consumer<String> onToken) {
        CompletableFuture<String> done = new CompletableFuture<>();
        TokenStream tokens = setu.chat(question);
        tokens.onPartialResponse(onToken)
                .onCompleteResponse(response -> done.complete(response.aiMessage().text()))
                .onError(done::completeExceptionally)
                .start();
        return done;
    }
}
