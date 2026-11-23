package com.atlas;

import java.util.List;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.SafeGuardAdvisor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Atlas on the lobby screen, where most visitors are children: guarded before the model is ever called. */
@RestController
public class AskController {

    /** Personal details a child should never type into a public screen. */
    static final List<String> PRIVATE_WORDS = List.of("my address", "my phone number", "my password", "my school is");

    static final String PRIVACY_REPLY = "Please keep personal details like addresses, phone numbers and passwords to yourself. "
            + "I am the museum's guide: ask me about the exhibits!";

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
                .defaultAdvisors(
                        SafeGuardAdvisor.builder()
                                .sensitiveWords(PRIVATE_WORDS)
                                .failureResponse(PRIVACY_REPLY)
                                .order(0)
                                .build(),
                        new QuestionLimitAdvisor(300))
                .build();
    }

    @GetMapping("/ask")
    public String ask(@RequestParam String q) {
        return chat.prompt()
                .user(q)
                .call()
                .content();
    }
}
