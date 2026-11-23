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

    // TODO (task stream_tokens): call model.chat(question, handler) with a StreamingChatResponseHandler that passes
    //   each partial response to onToken, completes the future with the ChatResponse when the answer is complete,
    //   and completes it exceptionally on an error. Return the future.
    public static CompletableFuture<ChatResponse> stream(StreamingChatModel model, String question, Consumer<String> onToken) {
        return new CompletableFuture<>();
    }

    // TODO (task token_stream): start setu.chat(question), a TokenStream: onPartialResponse(onToken), then complete
    //   the future with the whole answer's text on onCompleteResponse, completeExceptionally on onError, and start().
    public static CompletableFuture<String> ask(StreamingAssistant setu, String question, Consumer<String> onToken) {
        return new CompletableFuture<>();
    }
}
