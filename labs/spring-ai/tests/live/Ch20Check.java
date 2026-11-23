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

/** Chapter 20: the whole of Atlas in one ChatClient, behind the lobby screen's API. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch20Check {
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

    JsonNode send(String visitor, String text) throws Exception {
        String body = JSON.writeValueAsString(java.util.Map.of("visitor", visitor, "text", text));
        return JSON.readTree(mvc.perform(post("/chat").contentType("application/json").content(body)).andReturn().getResponse().getContentAsString());
    }

    @Test
    void assembleAtlas() {
        R.task("assemble_atlas", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text("The wire is 15 metres long.");
            send("check-a" + System.nanoTime(), "How long is the wire of the Foucault pendulum?");
            if (AI.chatRequests.isEmpty()) {
                R.fail("assemble_atlas", "the model was never called for an ordinary question.");
                return;
            }
            JsonNode req = AI.chat(-1);
            List<String> tools = FakeOpenAi.tools(req);
            if (!tools.contains("openingHours") || !tools.contains("planetariumShows")) {
                R.fail("assemble_atlas", "Atlas was not offered the museum's tools: add .defaultTools(tools).", "openingHours, planetariumShows, ...", tools.toString());
                return;
            }
            if (!text(req, "user").contains("15 metre steel wire")) {
                R.fail("assemble_atlas", "the pendulum card did not travel with the question: add the QuestionAnswerAdvisor (top 3, at least 0.35).");
                return;
            }
            String ria = "check-r" + System.nanoTime();
            send(ria, "Where is the planetarium?");
            send(ria, "And when are its shows?");
            if (!text(AI.chat(-1), "user").contains("Where is the planetarium?")) {
                R.fail("assemble_atlas", "the second message forgot the first: add the session advisors (SessionAdvisors.builder(sessions), 8 turns, then keep 4).");
                return;
            }
            int before = AI.chatRequests.size();
            JsonNode privacy = send("check-b" + System.nanoTime(), "my phone number is 98220 12345");
            if (AI.chatRequests.size() != before || !privacy.toString().contains("Please keep personal details")) {
                R.fail("assemble_atlas", "a phone number reached the model: add the SafeGuardAdvisor with PRIVATE_WORDS and PRIVACY_REPLY.");
                return;
            }
            JsonNode tooLong = send("check-c" + System.nanoTime(), "Tell me everything about the museum. ".repeat(10));
            if (AI.chatRequests.size() != before || !tooLong.toString().contains("too long")) {
                R.fail("assemble_atlas", "a 370-character question reached the model: add new QuestionLimitAdvisor(300).");
                return;
            }
            R.pass("assemble_atlas", "One ChatClient with everything: tools, the cards, memory, the privacy guard and the length limit.");
        });
    }

    @Test
    void liveChat() {
        R.task("live_chat", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text("The wire is 15 metres long.");
            String ria = "ria" + System.nanoTime();
            JsonNode first = send(ria, "How long is the wire of the Foucault pendulum?");
            if (!first.path("sources").toString().contains("foucault-pendulum.md")) {
                R.fail("live_chat", "sources should list the files of the retrieved cards, from response.context().get(QuestionAnswerAdvisor.RETRIEVED_DOCUMENTS).", "[\"foucault-pendulum.md\"]", first.path("sources").toString());
                return;
            }
            send(ria, "And how heavy is the ball on the pendulum?");
            if (!text(AI.chat(-1), "user").contains("How long is the wire")) {
                R.fail("live_chat", "the second message forgot the first. Keep .advisors(SessionAdvisors.session(message.visitor())) on the call.");
                return;
            }
            send("sam" + System.nanoTime(), "Where is the pendulum?");
            if (text(AI.chat(-1), "user").contains("How long is the wire")) {
                R.fail("live_chat", "Sam's question carried Ria's conversation: use message.visitor() as the session id.");
                return;
            }
            R.pass("live_chat", "Atlas is live: each visitor has their own conversation, and every answer names the cards it came from.");
        });
    }
}
