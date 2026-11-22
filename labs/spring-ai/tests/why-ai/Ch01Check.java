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

/** Chapter 1: the first call, and the model alias. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch01Check {
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
    void firstCall() {
        R.task("first_call", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text("The planetarium show starts at 4 pm.");
            String body = call("/ask?q=When is the planetarium show?");
            if (AI.chatRequests.isEmpty()) {
                R.fail("first_call", "GET /ask never called the model. Build the request with chat.prompt(), add the visitor's question with .user(q), then .call().content().", "the model's answer", body);
                return;
            }
            var users = FakeOpenAi.texts(AI.chat(-1), "user");
            if (users.isEmpty() || !users.get(users.size() - 1).equals("When is the planetarium show?")) {
                R.fail("first_call", "the model was called, but the visitor's question was not sent as the user message.", "When is the planetarium show?", users.toString());
                return;
            }
            if (!body.equals("The planetarium show starts at 4 pm.")) {
                R.fail("first_call", "the question reached the model, but /ask did not return the model's answer.", "The planetarium show starts at 4 pm.", body);
                return;
            }
            R.pass("first_call", "Atlas asked the model and returned its answer: your first AI endpoint.");
        });
    }

    @Test
    void modelAlias() {
        R.task("model_alias", () -> {
            AI.reset();
            call("/ask?q=Hello");
            if (AI.chatRequests.isEmpty()) {
                R.fail("model_alias", "first make /ask call the model (the task before this one), so the check can see which model it asks for.");
                return;
            }
            String model = AI.chat(-1).path("model").asString("");
            if (!model.equals("ai-chat")) {
                R.fail("model_alias", "the request asks for a model the LabBox gateway does not know. Set spring.ai.openai.chat.options.model in application.properties.", "ai-chat", model);
                return;
            }
            R.pass("model_alias", "Every request now names ai-chat, the model LabBox gives this course.");
        });
    }
}
