package com.setu.check;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Local;
import com.sun.net.httpserver.HttpServer;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;

class Ch24Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    /** A tiny stand-in for Ollama's own API (/api/chat). */
    static final class FakeOllama implements AutoCloseable {
        final List<String> bodies = new CopyOnWriteArrayList<>();
        final HttpServer server;

        FakeOllama() throws IOException {
            server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
            server.createContext("/api/chat", ex -> {
                bodies.add(new String(ex.getRequestBody().readAllBytes(), StandardCharsets.UTF_8));
                byte[] out = ("{\"model\":\"qwen2.5:0.5b\",\"created_at\":\"2026-11-23T10:00:00Z\",\"message\":{\"role\":\"assistant\","
                        + "\"content\":\"A hill railway climbs mountains.\"},\"done\":true,\"done_reason\":\"stop\",\"prompt_eval_count\":12,\"eval_count\":6}").getBytes(StandardCharsets.UTF_8);
                ex.getResponseHeaders().add("Content-Type", "application/json");
                ex.sendResponseHeaders(200, out.length);
                try (OutputStream o = ex.getResponseBody()) { o.write(out); }
            });
            server.start();
        }

        String url() { return "http://127.0.0.1:" + server.getAddress().getPort(); }

        @Override
        public void close() { server.stop(0); }
    }

    @Test
    void ollamaModel() {
        R.task("ollama_model", () -> {
            try (FakeOllama ollama = new FakeOllama()) {
                ChatModel model = Local.ollama(ollama.url(), "qwen2.5:0.5b");
                if (model == null) {
                    R.fail("ollama_model", "Local.ollama returned null. Build an OllamaChatModel with baseUrl(baseUrl), modelName(modelName) and temperature(0.0).");
                    return;
                }
                String got = model.chat("What is a hill railway?");
                if (ollama.bodies.isEmpty() || !ollama.bodies.get(0).contains("qwen2.5:0.5b")) {
                    R.fail("ollama_model", "The request did not reach Ollama with the model name: use .baseUrl(baseUrl) and .modelName(modelName).");
                    return;
                }
                if (!ollama.bodies.get(0).replace(" ", "").contains("\"temperature\":0.0")) {
                    R.fail("ollama_model", "Set .temperature(0.0) too, so the local model answers steadily.");
                    return;
                }
                if (!"A hill railway climbs mountains.".equals(got)) {
                    R.fail("ollama_model", "chat(...) should return Ollama's answer.", "A hill railway climbs mountains.", String.valueOf(got));
                    return;
                }
            }
            R.pass("ollama_model", "Same ChatModel interface, different engine: an open model on your own machine, no key and no bill per token.");
        });
    }

    @Test
    void routingModel() {
        R.task("routing_model", () -> {
            FAKE.reset();
            ChatModel small = OpenAiChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("small-model").build();
            ChatModel large = OpenAiChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("large-model").build();
            ChatModel routed = Local.routing(small, large);
            routed.chat("Hi!");
            String first = FAKE.chat(-1).path("model").asString();
            routed.chat("x".repeat(200));
            String second = FAKE.chat(-1).path("model").asString();
            if (!"small-model".equals(first)) {
                R.fail("routing_model", "\"Hi!\" went to " + first + "; short messages should go to the small model. Build a RoutingChatModel with routes simple and complex and the length rule from the TODO.", "small-model", first);
                return;
            }
            if (!"large-model".equals(second)) {
                R.fail("routing_model", "A 200-character message went to " + second + "; messages over 120 characters should go to the large model.", "large-model", second);
                return;
            }
            R.pass("routing_model", "One ChatModel that picks the right model per request: cheap for greetings, capable for the hard ones.");
        });
    }
}
