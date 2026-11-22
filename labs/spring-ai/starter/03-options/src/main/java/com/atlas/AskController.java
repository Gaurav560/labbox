package com.atlas;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.metadata.Usage;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.openai.OpenAiChatOptions;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Atlas answers visitors' questions, with settled options, and can report what an answer cost. */
@RestController
public class AskController {

    /** An answer with the tokens it used. */
    public record CostedAnswer(String answer, int promptTokens, int completionTokens, int totalTokens) {}

    private final ChatClient chat;

    public AskController(ChatClient.Builder builder) {
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
        // TODO (task chat_options): steady, short answers: temperature 0.2, at most 300 tokens.
        return chat.prompt()
                .user(q)
                .call()
                .content();
    }

    /** GET /ask/costed?q=... answers, and says how many tokens the answer used. */
    @GetMapping("/ask/costed")
    public CostedAnswer costed(@RequestParam String q) {
        // TODO (task token_usage): call the model, then read the answer and its token usage from the ChatResponse.
        return new CostedAnswer("Not written yet.", 0, 0, 0);
    }
}
