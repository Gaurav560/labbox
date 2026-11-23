package com.atlas.check;

import java.util.ArrayList;
import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

/** Chapter 18: tokens and cost of each answer, and the AI metrics Spring AI records. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch18Check {
    static final FakeOpenAi AI = new FakeOpenAi();
    static final JsonMapper JSON = JsonMapper.builder().build();

    @DynamicPropertySource
    static void ai(DynamicPropertyRegistry r) {
        r.add("spring.ai.openai.base-url", AI::baseUrl);
        r.add("spring.ai.openai.api-key", () -> "check-key");
    }

    @AfterAll
    static void stop() {
        AI.stop();
    }

    @Autowired
    MockMvc mvc;

    String call(String path, String... params) throws Exception {
        var req = get(path);
        for (int i = 0; i + 1 < params.length; i += 2) req = req.param(params[i], params[i + 1]);
        return mvc.perform(req).andReturn().getResponse().getContentAsString();
    }

    /** All the text of the messages with this role in a request, whether plain or in parts. */
    static String text(JsonNode request, String role) {
        StringBuilder b = new StringBuilder();
        for (JsonNode m : request.path("messages")) {
            if (!role.equals(m.path("role").asString())) continue;
            JsonNode c = m.path("content");
            if (c.isArray()) {
                for (JsonNode p : c) b.append(p.path("text").asString("")).append(" ");
            } else {
                b.append(c.asString("")).append(" ");
            }
        }
        return b.toString();
    }

    static String cut(String s) {
        return s.length() > 160 ? s.substring(0, 160) + "..." : s;
    }

    @Test
    void tokenUsage() {
        R.task("answer_cost", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text("Open from 10:00 to 18:00.");
            JsonNode r = JSON.readTree(call("/ask/metered", "q", "When are you open?"));
            if (!"Open from 10:00 to 18:00.".equals(r.path("answer").asString(""))) {
                R.fail("answer_cost", "answer should hold the model's text.", "Open from 10:00 to 18:00.", cut(r.toString()));
                return;
            }
            if (r.path("promptTokens").asInt() != 42 || r.path("completionTokens").asInt() != 8) {
                R.fail("answer_cost", "read the tokens from response.getMetadata().getUsage(): getPromptTokens() and getCompletionTokens().", "promptTokens 42, completionTokens 8", cut(r.toString()));
                return;
            }
            double expected = 42 * 0.15 / 1_000_000 + 8 * 0.60 / 1_000_000;
            if (Math.abs(r.path("costUsd").asDouble() - expected) > 1e-12) {
                R.fail("answer_cost", "cost = prompt tokens times 0.15 per million, plus completion tokens times 0.60 per million.", String.valueOf(expected), r.path("costUsd").toString());
                return;
            }
            R.pass("answer_cost", "Every answer now carries its meter: 42 tokens in, 8 out, 0.0000111 dollars.");
        });
    }

    @Test
    void aiMetrics() {
        R.task("ai_metrics", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text("Hello!");
            call("/ask", "q", "Hello");
            var res = mvc.perform(get("/actuator/metrics/gen_ai.client.token.usage")).andReturn().getResponse();
            if (res.getStatus() == 404) {
                R.fail("ai_metrics", "/actuator/metrics was not found. Expose it in application.properties: management.endpoints.web.exposure.include=health,metrics.");
                return;
            }
            String body = res.getContentAsString();
            if (res.getStatus() != 200 || !body.contains("measurements")) {
                R.fail("ai_metrics", "the token metric should be readable after one call.", "200 with measurements", res.getStatus() + " " + cut(body));
                return;
            }
            var health = mvc.perform(get("/actuator/health")).andReturn().getResponse();
            if (health.getStatus() != 200) {
                R.fail("ai_metrics", "expose health too: management.endpoints.web.exposure.include=health,metrics.");
                return;
            }
            R.pass("ai_metrics", "Spring AI counts every token it sends and receives: gen_ai.client.token.usage is live on /actuator/metrics.");
        });
    }
}
