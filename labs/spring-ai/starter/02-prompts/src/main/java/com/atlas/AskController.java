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
        // TODO (task system_prompt): give every conversation a system prompt: who Atlas is, where, and the rules.
        this.chat = builder.build();
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
        // TODO (task prompt_template): ask the model to explain the exhibit for a visitor of that age, with a template.
        return "Not written yet.";
    }
}
