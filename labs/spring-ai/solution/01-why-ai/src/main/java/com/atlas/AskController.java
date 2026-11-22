package com.atlas;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Atlas answers visitors' questions: GET /ask?q=... */
@RestController
public class AskController {

    private final ChatClient chat;

    public AskController(ChatClient.Builder builder) {
        this.chat = builder.build();
    }

    @GetMapping("/ask")
    public String ask(@RequestParam String q) {
        return chat.prompt()
                .user(q)
                .call()
                .content();
    }
}
