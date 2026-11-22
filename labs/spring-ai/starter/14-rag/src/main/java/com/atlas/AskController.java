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
                // TODO (task rag_answer): retrieve the 3 closest chunks (similarity at least 0.35) for every question.
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
        // TODO (task cite_sources): call, keep the ChatClientResponse, and list the files of the retrieved documents.
        return new SourcedAnswer(ask(q), List.of());
    }
}
