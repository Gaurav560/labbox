package com.atlas;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Atlas answers visitors' questions, and explains exhibits for any age. */
@RestController
public class AskController {

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
        return chat.prompt()
                .user(q)
                .call()
                .content();
    }

    /** GET /explain?exhibit=Foucault pendulum&age=9 */
    @GetMapping("/explain")
    public String explain(@RequestParam String exhibit, @RequestParam int age) {
        return chat.prompt()
                .user(u -> u.text("Explain the exhibit {exhibit} to a visitor who is {age} years old.")
                        .param("exhibit", exhibit)
                        .param("age", age))
                .call()
                .content();
    }
}
