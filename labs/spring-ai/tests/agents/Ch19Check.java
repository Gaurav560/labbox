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

import java.util.concurrent.atomic.AtomicInteger;

/** Chapter 19: a routing workflow and an evaluator-optimizer loop. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch19Check {
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
    void routeQuestion() {
        R.task("route_question", () -> {
            String[][] cases = {{"VISIT", "Are you open on Sunday?", "front desk"}, {"EXHIBITS", "Why does the pendulum turn?", "science explainer"}};
            for (String[] c : cases) {
                AI.reset();
                AI.script = b -> b.contains("You sort visitor questions") ? FakeOpenAi.Reply.text("{\"desk\": \"" + c[0] + "\"}") : FakeOpenAi.Reply.text("An answer from the desk.");
                JsonNode r = JSON.readTree(call("/agent/route", "q", c[1]));
                if (AI.chatRequests.size() != 2) {
                    R.fail("route_question", "routing takes two calls: one to choose the desk (ROUTER), one to answer as that desk.", "2 calls", AI.chatRequests.size() + " calls");
                    return;
                }
                if (!text(AI.chat(0), "system").contains("You sort visitor questions")) {
                    R.fail("route_question", "the first call should use the ROUTER system prompt and return a Routing.");
                    return;
                }
                if (!c[0].equals(r.path("desk").asString(""))) {
                    R.fail("route_question", "desk should be the router's choice.", c[0], cut(r.toString()));
                    return;
                }
                if (!text(AI.chat(1), "system").contains(c[2])) {
                    R.fail("route_question", "the second call should use the chosen desk's prompt, DESKS.get(desk).", "the " + c[0] + " desk's prompt", cut(text(AI.chat(1), "system")));
                    return;
                }
            }
            R.pass("route_question", "Each question goes to the right desk first: the front desk for hours, the explainer for science.");
        });
    }

    @Test
    void improveLoop() {
        R.task("improve_loop", () -> {
            AI.reset();
            AtomicInteger drafts = new AtomicInteger();
            AtomicInteger reviews = new AtomicInteger();
            AI.script = b -> b.contains("You review exhibit labels")
                    ? FakeOpenAi.Reply.text(reviews.incrementAndGet() == 1 ? "{\"approved\": false, \"feedback\": \"Too long: cut it to 40 words.\"}" : "{\"approved\": true, \"feedback\": \"Good.\"}")
                    : FakeOpenAi.Reply.text("Draft " + drafts.incrementAndGet());
            JsonNode r = JSON.readTree(call("/agent/label", "exhibit", "Prism room"));
            if (reviews.get() == 0) {
                R.fail("improve_loop", "the draft was never reviewed. Ask the REVIEWER for a Review of the draft.");
                return;
            }
            if (!"Draft 2".equals(r.path("text").asString("")) || r.path("drafts").asInt() != 2) {
                R.fail("improve_loop", "after a rejected first draft, rewrite once and stop when the second is approved.", "{\"text\":\"Draft 2\",\"drafts\":2}", cut(r.toString()));
                return;
            }
            boolean feedbackSent = AI.chatRequests.stream().anyMatch(b -> !b.contains("You review exhibit labels") && b.contains("Too long: cut it to 40 words."));
            if (!feedbackSent) {
                R.fail("improve_loop", "the rewrite should include the reviewer's feedback, so the writer knows what to change.");
                return;
            }
            AI.reset();
            AI.script = b -> b.contains("You review exhibit labels")
                    ? FakeOpenAi.Reply.text("{\"approved\": false, \"feedback\": \"Still too hard.\"}")
                    : FakeOpenAi.Reply.text("Another draft");
            JsonNode never = JSON.readTree(call("/agent/label", "exhibit", "Prism room"));
            if (never.path("drafts").asInt() != 3 || AI.chatRequests.size() > 6) {
                R.fail("improve_loop", "when the reviewer never approves, stop after 3 drafts.", "3 drafts, at most 6 calls", never.path("drafts") + " drafts, " + AI.chatRequests.size() + " calls");
                return;
            }
            R.pass("improve_loop", "Write, review, rewrite: the label improved with the reviewer's feedback, and the loop always ends.");
        });
    }
}
