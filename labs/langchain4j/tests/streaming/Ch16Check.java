package com.setu.check;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.StreamingAssistant;
import com.setu.Streams;

import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.openai.OpenAiStreamingChatModel;
import dev.langchain4j.service.AiServices;

class Ch16Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();
    static final String ANSWER = "Trains slow down on a ghat because the climb is steep.";

    @AfterAll
    static void stop() { FAKE.stop(); }

    static StreamingChatModel model() {
        return OpenAiStreamingChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-chat").build();
    }

    @Test
    void streamTokens() {
        R.task("stream_tokens", () -> {
            FAKE.reset();
            FAKE.script = b -> FakeOpenAi.Reply.text(ANSWER);
            List<String> pieces = new ArrayList<>();
            CompletableFuture<ChatResponse> f = Streams.stream(model(), "Why slow?", pieces::add);
            ChatResponse r;
            try {
                r = f.get(10, TimeUnit.SECONDS);
            } catch (java.util.concurrent.TimeoutException e) {
                R.fail("stream_tokens", "The future never completed. Call model.chat(question, handler), and in onCompleteResponse complete the future with the ChatResponse.");
                return;
            }
            if (pieces.size() < 2) {
                R.fail("stream_tokens", "onToken got " + pieces.size() + " pieces. In onPartialResponse, pass each piece to onToken.accept(...).", "one call per piece", String.valueOf(pieces));
                return;
            }
            if (!ANSWER.equals(String.join("", pieces)) || r == null || !ANSWER.equals(r.aiMessage().text())) {
                R.fail("stream_tokens", "The pieces, joined, should be the whole answer, and the future should hold the complete ChatResponse.", ANSWER, String.join("", pieces));
                return;
            }
            R.pass("stream_tokens", "Each piece arrived as the model wrote it, then the complete response with its usage: streaming, the low-level way.");
        });
    }

    @Test
    void tokenStream() {
        R.task("token_stream", () -> {
            FAKE.reset();
            FAKE.script = b -> FakeOpenAi.Reply.text(ANSWER);
            StreamingAssistant setu = AiServices.create(StreamingAssistant.class, model());
            List<String> pieces = new ArrayList<>();
            String got;
            try {
                got = Streams.ask(setu, "Why slow?", pieces::add).get(10, TimeUnit.SECONDS);
            } catch (java.util.concurrent.TimeoutException e) {
                R.fail("token_stream", "The future never completed. A TokenStream does nothing until start(): set onPartialResponse, onCompleteResponse and onError, then call start().");
                return;
            }
            if (pieces.size() < 2 || !ANSWER.equals(String.join("", pieces))) {
                R.fail("token_stream", "Pass each partial response to onToken with onPartialResponse(onToken).", ANSWER, String.join("", pieces));
                return;
            }
            if (!ANSWER.equals(got)) {
                R.fail("token_stream", "Complete the future with the whole answer's text: response.aiMessage().text() in onCompleteResponse.", ANSWER, String.valueOf(got));
                return;
            }
            R.pass("token_stream", "An AI Service that streams: the method returns a TokenStream, and start() sets the words flowing.");
        });
    }
}
