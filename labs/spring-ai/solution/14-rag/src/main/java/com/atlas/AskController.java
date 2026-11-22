package com.atlas;

import java.util.List;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.ChatClientResponse;
import org.springframework.ai.chat.client.advisor.vectorstore.QuestionAnswerAdvisor;
import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Atlas answers from the museum's own exhibit cards, and says which cards it used. */
@RestController
public class AskController {

    /** An answer, with the cards it was based on. */
    public record SourcedAnswer(String answer, List<String> sources) {}

    private final ChatClient chat;

    public AskController(ChatClient.Builder builder, VectorStore store) {
        this.chat = builder
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

    @GetMapping("/ask")
    public String ask(@RequestParam String q) {
        return chat.prompt()
                .user(q)
                .call()
                .content();
    }

    /** GET /ask/sourced?q=... the answer, and the files of the cards that were retrieved for it. */
    @GetMapping("/ask/sourced")
    public SourcedAnswer sourced(@RequestParam String q) {
        ChatClientResponse response = chat.prompt()
                .user(q)
                .call()
                .chatClientResponse();
        @SuppressWarnings("unchecked")
        List<Document> used = (List<Document>) response.context().get(QuestionAnswerAdvisor.RETRIEVED_DOCUMENTS);
        List<String> files = used == null ? List.of()
                : used.stream().map(d -> (String) d.getMetadata().get("file")).distinct().toList();
        return new SourcedAnswer(response.chatResponse().getResult().getOutput().getText(), files);
    }
}
