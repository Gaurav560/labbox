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

/** Chapter 2: the system prompt, and a prompt template. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch02Check {
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
    void systemPrompt() {
        R.task("system_prompt", () -> {
            AI.reset();
            call("/ask?q=Is the museum open today?");
            var systems = FakeOpenAi.texts(AI.chat(-1), "system");
            if (systems.isEmpty()) {
                R.fail("system_prompt", "requests have no system message yet. Give the ChatClient a default one with builder.defaultSystem(...) before build().");
                return;
            }
            String s = String.join(" ", systems).toLowerCase();
            if (!s.contains("atlas") || !s.contains("deccan science museum")) {
                R.fail("system_prompt", "the system prompt should say who the model is (Atlas) and where (the Deccan Science Museum).", "Atlas ... Deccan Science Museum ...", String.join(" ", systems));
                return;
            }
            if (s.contains("is the museum open today")) {
                R.fail("system_prompt", "the visitor's question ended up inside the system prompt. Keep it in the user message: the system prompt is your rules, the user message is theirs.");
                return;
            }
            R.pass("system_prompt", "Every conversation now starts with Atlas's own rules, in a system message the visitor cannot see.");
        });
    }

    @Test
    void promptTemplate() {
        R.task("prompt_template", () -> {
            AI.reset();
            String body = mvc.perform(get("/explain").param("exhibit", "Foucault pendulum").param("age", "9")).andReturn().getResponse().getContentAsString();
            if (AI.chatRequests.isEmpty()) {
                R.fail("prompt_template", "GET /explain never called the model.", "a call with the exhibit and the age", body);
                return;
            }
            var users = FakeOpenAi.texts(AI.chat(-1), "user");
            String u = users.isEmpty() ? "" : users.get(users.size() - 1);
            if (u.contains("{") || u.contains("}")) {
                R.fail("prompt_template", "a placeholder was sent to the model unfilled. Every {name} in the template needs a .param(\"name\", value).", "the exhibit and the age filled in", u);
                return;
            }
            if (!u.contains("Foucault pendulum") || !u.contains("9")) {
                R.fail("prompt_template", "the user message should name the exhibit and the visitor's age.", "... Foucault pendulum ... 9 ...", u);
                return;
            }
            if (FakeOpenAi.texts(AI.chat(-1), "system").isEmpty()) {
                R.fail("prompt_template", "the explanation was asked without Atlas's system prompt. Keep defaultSystem on the ChatClient so every request gets it.");
                return;
            }
            R.pass("prompt_template", "The template filled in the exhibit and the age; the system prompt came along by itself.");
        });
    }
}
