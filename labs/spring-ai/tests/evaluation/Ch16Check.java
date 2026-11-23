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

import com.atlas.Golden;
import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;

/** Chapter 16: measuring retrieval on golden questions, and a judge model for answers. */
@SpringBootTest
@AutoConfigureMockMvc
class Ch16Check {
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

    @Autowired
    VectorStore store;

    @Test
    void retrievalEval() {
        R.task("retrieval_eval", () -> {
            AI.reset();
            int hits = 0;
            List<String> misses = new ArrayList<>();
            for (Golden g : Golden.QUESTIONS) {
                List<Document> found = store.similaritySearch(SearchRequest.builder().query(g.question()).topK(3).similarityThreshold(0.35).build());
                if (found.stream().anyMatch(d -> g.file().equals(d.getMetadata().get("file")))) hits++;
                else misses.add(g.question());
            }
            JsonNode r = JSON.readTree(call("/eval/retrieval"));
            if (r.path("total").asInt(-1) != Golden.QUESTIONS.size()) {
                R.fail("retrieval_eval", "total should count every golden question.", String.valueOf(Golden.QUESTIONS.size()), r.path("total").toString());
                return;
            }
            if (r.path("hits").asInt(-1) != hits) {
                R.fail("retrieval_eval", "a golden question is a hit when its file is among the 3 closest chunks with a similarity of at least 0.35.", hits + " hits", r.path("hits").toString() + " hits");
                return;
            }
            List<String> got = new ArrayList<>();
            for (JsonNode m : r.path("misses")) got.add(m.asString());
            if (!got.equals(misses)) {
                R.fail("retrieval_eval", "misses should list the questions whose card was not found, in order.", misses.toString(), got.toString());
                return;
            }
            R.pass("retrieval_eval", "Retrieval measured: " + hits + " of " + Golden.QUESTIONS.size() + " golden questions found their card. Now every change can be compared with this number.");
        });
    }

    @Test
    void judgeAnswer() {
        R.task("judge_answer", () -> {
            for (String verdict : List.of("YES", "NO")) {
                AI.reset();
                AI.script = b -> b.contains("Your task is to evaluate") ? FakeOpenAi.Reply.text(verdict) : FakeOpenAi.Reply.text("The wire is 15 metres long.");
                JsonNode r = JSON.readTree(call("/ask/judged", "q", "How long is the wire of the Foucault pendulum?"));
                String judgeRequest = AI.chatRequests.stream().filter(b -> b.contains("Your task is to evaluate")).findFirst().orElse("");
                if (judgeRequest.isEmpty()) {
                    R.fail("judge_answer", "no judge was asked. Evaluate the answer with a RelevancyEvaluator built on its own ChatClient.");
                    return;
                }
                if (!judgeRequest.contains("The wire is 15 metres long.") || !judgeRequest.contains("15 metre steel wire")) {
                    R.fail("judge_answer", "the judge should see the question, the answer and the retrieved cards: new EvaluationRequest(q, used, answer).");
                    return;
                }
                if (judgeRequest.contains("Context information is below")) {
                    R.fail("judge_answer", "the judge's ChatClient carries Atlas's RAG advisor. Build the judge on a fresh ChatClient.builder(model).");
                    return;
                }
                boolean expected = verdict.equals("YES");
                if (r.path("relevant").asBoolean(!expected) != expected) {
                    R.fail("judge_answer", "relevant should be the judge's verdict, evaluate(...).isPass().", "relevant " + expected + " when the judge says " + verdict, cut(r.toString()));
                    return;
                }
            }
            R.pass("judge_answer", "A second model now grades every answer against the question and the cards: YES passes, NO is flagged.");
        });
    }
}
