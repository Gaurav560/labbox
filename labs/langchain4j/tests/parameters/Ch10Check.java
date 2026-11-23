package com.setu.check;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Tuned;

import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.openai.OpenAiChatModel;
import tools.jackson.databind.JsonNode;

class Ch10Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    @Test
    void steadyModel() {
        R.task("steady_model", () -> {
            FAKE.reset();
            Tuned.steadyModel(FAKE.baseUrl(), "k").chat("A slogan, please.");
            JsonNode req = FAKE.chat(-1);
            JsonNode t = req.path("temperature");
            if (t.isMissingNode() || t.isNull()) {
                R.fail("steady_model", "The request has no temperature, so the model uses its default (1.0). Add .temperature(0.0) to the builder.", "temperature 0.0", "not set");
                return;
            }
            if (t.asDouble() != 0.0) {
                R.fail("steady_model", "Temperature should be 0.0 for steady, repeatable answers.", "0.0", t.asString());
                return;
            }
            if (!"ai-chat".equals(req.path("model").asString())) {
                R.fail("steady_model", "Keep the model name \"ai-chat\".", "ai-chat", req.path("model").asString());
                return;
            }
            R.pass("steady_model", "Temperature 0: the likeliest token every time. Right for facts, timetables and data extraction.");
        });
    }

    @Test
    void shortAnswer() {
        R.task("short_answer", () -> {
            FAKE.reset();
            ChatModel model = OpenAiChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-chat").build();
            ChatResponse r = Tuned.ask(model, "Describe the journey to Ratnagiri.", 20);
            JsonNode req = FAKE.chat(-1);
            JsonNode max = req.has("max_completion_tokens") ? req.path("max_completion_tokens") : req.path("max_tokens");
            if (max.isMissingNode() || max.isNull()) {
                R.fail("short_answer", "The request has no limit on the answer's length. Build a ChatRequest with .messages(...) and .maxOutputTokens(maxTokens), then model.chat(request).", "20", "no limit");
                return;
            }
            if (max.asInt() != 20) {
                R.fail("short_answer", "Use the maxTokens parameter, not a fixed number.", "20", max.asString());
                return;
            }
            if (FakeOpenAi.texts(req, "system").isEmpty() || !FakeOpenAi.texts(req, "user").contains("Describe the journey to Ratnagiri.")) {
                R.fail("short_answer", "Keep both messages in the request: SystemMessage.from(SYSTEM) and UserMessage.from(question).");
                return;
            }
            if (r == null) {
                R.fail("short_answer", "Return the ChatResponse from model.chat(request).");
                return;
            }
            R.pass("short_answer", "A limit for one request, without changing the model: ChatRequest overrides the model's defaults.");
        });
    }
}
