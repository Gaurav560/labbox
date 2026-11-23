package com.atlas;

import java.util.ArrayList;
import java.util.List;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.ChatClientResponse;
import org.springframework.ai.chat.client.advisor.vectorstore.QuestionAnswerAdvisor;
import org.springframework.ai.chat.evaluation.RelevancyEvaluator;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.document.Document;
import org.springframework.ai.evaluation.EvaluationRequest;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** How good is Atlas? Measures retrieval on the golden questions, and lets a judge model check answers. */
@RestController
public class EvalController {

    /** How many golden questions found their card among the 3 retrieved, and which did not. */
    public record RetrievalReport(int total, int hits, List<String> misses) {}

    /** An answer, and the judge's verdict on it. */
    public record JudgedAnswer(String answer, boolean relevant) {}

    static final SearchRequest.Builder SEARCH = SearchRequest.builder().topK(3).similarityThreshold(0.35);

    private final VectorStore store;
    private final ChatModel model;
    private final ChatClient atlas;

    public EvalController(ChatClient.Builder builder, ChatModel model, VectorStore store) {
        this.store = store;
        this.model = model;
        this.atlas = builder
                .defaultSystem("""
            You are Atlas, the friendly visitor guide of the Deccan Science Museum in Pune.
            Answer in at most three short sentences, in plain, simple words.
            You may answer questions about the museum, its exhibits, and any science topic.
            For anything else, say kindly that you are the museum's guide.
            Never invent opening hours, prices or exhibits: if you do not know, say so.
            """)
                .defaultAdvisors(QuestionAnswerAdvisor.builder(store)
                        .searchRequest(SearchRequest.builder().topK(3).similarityThreshold(0.35).build())
                        .build())
                .build();
    }

    /** GET /eval/retrieval: for every golden question, is its card among the 3 chunks retrieved? */
    @GetMapping("/eval/retrieval")
    public RetrievalReport retrieval() {
        int hits = 0;
        List<String> misses = new ArrayList<>();
        for (Golden g : Golden.QUESTIONS) {
            List<Document> found = store.similaritySearch(SearchRequest.builder()
                    .query(g.question())
                    .topK(3)
                    .similarityThreshold(0.35)
                    .build());
            if (found.stream().anyMatch(d -> g.file().equals(d.getMetadata().get("file")))) {
                hits++;
            } else {
                misses.add(g.question());
            }
        }
        return new RetrievalReport(Golden.QUESTIONS.size(), hits, misses);
    }

    /** GET /ask/judged?q=... Atlas answers from the cards; a judge says whether the answer fits the question and the cards. */
    @GetMapping("/ask/judged")
    public JudgedAnswer judged(@RequestParam String q) {
        ChatClientResponse response = atlas.prompt()
                .user(q)
                .call()
                .chatClientResponse();
        @SuppressWarnings("unchecked")
        List<Document> used = (List<Document>) response.context().get(QuestionAnswerAdvisor.RETRIEVED_DOCUMENTS);
        String answer = response.chatResponse().getResult().getOutput().getText();
        RelevancyEvaluator judge = new RelevancyEvaluator(ChatClient.builder(model));
        EvaluationRequest request = new EvaluationRequest(q, used == null ? List.of() : used, answer);
        return new JudgedAnswer(answer, judge.evaluate(request).isPass());
    }
}
