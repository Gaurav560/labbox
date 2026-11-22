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
import com.atlas.Similarity;

/** Chapter 11: cosine similarity, and the nearest exhibit by meaning. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch11Check {
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

    @Test
    void cosineSimilarity() {
        R.task("cosine_similarity", () -> {
            float[][][] cases = {{{1, 0}, {1, 0}}, {{1, 0}, {0, 1}}, {{1, 2, 3}, {2, 4, 6}}, {{1, 0}, {-1, 0}}, {{0.3f, 0.4f, 0.5f}, {0.5f, 0.1f, 0.2f}}};
            double[] want = {1, 0, 1, -1, 0.7487828};
            for (int i = 0; i < cases.length; i++) {
                double got = Similarity.cosine(cases[i][0], cases[i][1]);
                if (Math.abs(got - want[i]) > 1e-4) {
                    R.fail("cosine_similarity", "cosine(" + java.util.Arrays.toString(cases[i][0]) + ", " + java.util.Arrays.toString(cases[i][1]) + ") is wrong. Divide the dot product by both lengths (square roots of the sums of squares).", String.format("%.4f", want[i]), String.format("%.4f", got));
                    return;
                }
            }
            R.pass("cosine_similarity", "Same direction 1, unrelated 0, opposite -1, and a real case right to four decimals.");
        });
    }

    @Test
    void nearestExhibit() {
        R.task("nearest_exhibit", () -> {
            AI.reset();
            String dino = call("/nearest", "q", "Tell me about the dinosaur");
            String dome = call("/nearest", "q", "Is there a planetarium show?");
            if (AI.embeddingRequests.isEmpty()) {
                R.fail("nearest_exhibit", "GET /nearest never asked the embedding model for anything. Embed the question and the descriptions with embeddings.embed(...).", "Rajasaurus", dino);
                return;
            }
            if (!"Rajasaurus".equals(dino) || !"Planetarium dome".equals(dome)) {
                R.fail("nearest_exhibit", "the nearest exhibit was not the most similar one. Compare the question's vector with each description's using Similarity.cosine, and keep the highest.", "Rajasaurus, Planetarium dome", dino + ", " + dome);
                return;
            }
            R.pass("nearest_exhibit", "A dinosaur question found Rajasaurus, a show question found the planetarium: search by meaning, with numbers.");
        });
    }
}
