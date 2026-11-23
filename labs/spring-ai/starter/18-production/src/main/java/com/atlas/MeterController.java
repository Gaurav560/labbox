package com.atlas;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.metadata.Usage;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Atlas, with a meter: every answer says how many tokens it used and what it cost. */
@RestController
public class MeterController {

    /** An answer, its tokens, and its cost in US dollars. */
    public record MeteredAnswer(String answer, int promptTokens, int completionTokens, double costUsd) {}

    /** gpt-4o-mini's price: US dollars per million tokens (OpenAI's price list, 2026). */
    static final double INPUT_PER_MILLION = 0.15;
    static final double OUTPUT_PER_MILLION = 0.60;

    private final ChatClient chat;

    public MeterController(ChatClient.Builder builder) {
        this.chat = builder
                .defaultSystem("""
            You are Atlas, the friendly visitor guide of the Deccan Science Museum in Pune.
            Answer in at most three short sentences, in plain, simple words.
            You may answer questions about the museum, its exhibits, and any science topic.
            For anything else, say kindly that you are the museum's guide.
            Never invent opening hours, prices or exhibits: if you do not know, say so.
            """)
                .build();
    }

    @GetMapping("/ask")
    public String ask(@RequestParam String q) {
        return chat.prompt().user(q).call().content();
    }

    /** GET /ask/metered?q=... the answer, with the tokens the model counted and their price. */
    @GetMapping("/ask/metered")
    public MeteredAnswer metered(@RequestParam String q) {
        // TODO (task answer_cost): call for the ChatResponse, read its usage (prompt and completion tokens) and work out the cost.
        return new MeteredAnswer(ask(q), 0, 0, 0);
    }
}
