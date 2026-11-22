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

/** Chapter 5: structured output into records and lists. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch05Check {
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
    void tourPlan() {
        R.task("tour_plan", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text("{\"title\":\"Space in an hour\",\"stops\":[{\"gallery\":\"Planetarium\",\"minutes\":30},{\"gallery\":\"Mars Yard\",\"minutes\":30}]}");
            String body = call("/tour?minutes=60");
            if (AI.chatRequests.isEmpty()) {
                R.fail("tour_plan", "GET /tour never called the model.", "a TourPlan", body);
                return;
            }
            String u = String.join(" ", FakeOpenAi.texts(AI.chat(-1), "user"));
            if (!u.contains("60")) {
                R.fail("tour_plan", "the request should say how long the tour may take (60 minutes here).", "... 60 ...", u);
                return;
            }
            if (!u.contains("\"gallery\"") || !u.contains("\"stops\"")) {
                R.fail("tour_plan", "the model was not told the shape to answer in. .entity(TourPlan.class) adds a JSON schema of the record to the request for you.");
                return;
            }
            JsonNode r = JSON.readTree(body);
            if (!"Space in an hour".equals(r.path("title").asString("")) || r.path("stops").size() != 2 || r.path("stops").get(0).path("minutes").asInt() != 30) {
                R.fail("tour_plan", "/tour should return the model's plan as a TourPlan.", "{title, stops: [2 stops]}", body);
                return;
            }
            R.pass("tour_plan", "The model's JSON became a TourPlan record, and Spring sent it back as JSON: data, not prose.");
        });
    }

    @Test
    void exhibitList() {
        R.task("exhibit_list", () -> {
            AI.reset();
            AI.script = b -> FakeOpenAi.Reply.text("{\"exhibits\":[\"Planetarium dome\",\"Mars rover model\",\"Moon rock\"]}");
            String body = call("/suggest?interest=space");
            if (AI.chatRequests.isEmpty()) {
                R.fail("exhibit_list", "GET /suggest never called the model.", "three names", body);
                return;
            }
            String u = String.join(" ", FakeOpenAi.texts(AI.chat(-1), "user"));
            if (!u.contains("space")) {
                R.fail("exhibit_list", "the request should mention the visitor's interest.", "... space ...", u);
                return;
            }
            if (!u.contains("\"exhibits\"") || !u.contains("\"array\"")) {
                R.fail("exhibit_list", "the model was not asked for the Suggestions shape. .entity(Suggestions.class) adds its JSON schema, with the exhibits list, to the request.");
                return;
            }
            JsonNode r = JSON.readTree(body);
            if (!r.isArray() || r.size() != 3 || !"Moon rock".equals(r.get(2).asString(""))) {
                R.fail("exhibit_list", "/suggest should return the model's three names as a JSON list.", "[\"Planetarium dome\", \"Mars rover model\", \"Moon rock\"]", body);
                return;
            }
            R.pass("exhibit_list", "A List<String> straight from the model, ready for the website to show as buttons.");
        });
    }
}
