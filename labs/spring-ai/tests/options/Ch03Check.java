package com.atlas.check;

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

/** Chapter 3: options, and token usage. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch03Check {
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

    String call(String url) throws Exception {
        return mvc.perform(get(url)).andReturn().getResponse().getContentAsString();
    }

    @Test
    void chatOptions() {
        R.task("chat_options", () -> {
            AI.reset();
            call("/ask?q=What is a pulsar?");
            JsonNode req = AI.chat(-1);
            double t = req.path("temperature").asDouble(-1);
            int max = req.has("max_tokens") ? req.path("max_tokens").asInt() : req.path("max_completion_tokens").asInt(-1);
            if (Math.abs(t - 0.2) > 1e-9) {
                R.fail("chat_options", "the request's temperature is not 0.2. Add .options(OpenAiChatOptions.builder().temperature(0.2)...) to the prompt.", "0.2", t < 0 ? "not set" : String.valueOf(t));
                return;
            }
            if (max != 300) {
                R.fail("chat_options", "the answer's length is not capped at 300 tokens. The same options builder has maxTokens(...).", "300", max < 0 ? "not set" : String.valueOf(max));
                return;
            }
            R.pass("chat_options", "Steady (temperature 0.2) and short (300 tokens at most): every /ask now costs a known maximum.");
        });
    }

    @Test
    void tokenUsage() {
        R.task("token_usage", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text("A pulsar is a spinning dead star.");
            String body = call("/ask/costed?q=What is a pulsar?");
            if (AI.chatRequests.isEmpty()) {
                R.fail("token_usage", "GET /ask/costed never called the model.", "an answer with its token counts", body);
                return;
            }
            JsonNode r = JSON.readTree(body);
            if (!"A pulsar is a spinning dead star.".equals(r.path("answer").asString(""))) {
                R.fail("token_usage", "the answer field should hold the model's text: response.getResult().getOutput().getText().", "A pulsar is a spinning dead star.", r.path("answer").asString(""));
                return;
            }
            int p = r.path("promptTokens").asInt(), c = r.path("completionTokens").asInt(), t = r.path("totalTokens").asInt();
            if (p != 42 || c != 8 || t != 50) {
                R.fail("token_usage", "the token counts should come from response.getMetadata().getUsage().", "42, 8, 50", p + ", " + c + ", " + t);
                return;
            }
            R.pass("token_usage", "42 tokens in, 8 out, 50 in all: now Atlas can tell you what every answer cost.");
        });
    }
}
