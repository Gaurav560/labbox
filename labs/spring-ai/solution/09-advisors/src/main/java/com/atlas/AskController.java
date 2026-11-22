package com.atlas;

import java.util.Map;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Atlas answers in the visitor's language, and keeps a meter of every call. */
@RestController
public class AskController {

    private final ChatClient chat;
    private final UsageAdvisor usage;

    public AskController(ChatClient.Builder builder, UsageAdvisor usage) {
        this.usage = usage;
        this.chat = builder
                .defaultSystem("""
            You are Atlas, the friendly visitor guide of the Deccan Science Museum in Pune.
            Answer in at most three short sentences, in plain, simple words.
            You may answer questions about the museum, its exhibits, and any science topic.
            For anything else, say kindly that you are the museum's guide.
            Never invent opening hours, prices or exhibits: if you do not know, say so.
            """)
                .defaultAdvisors(usage, new LanguageAdvisor())
                .build();
    }

    /** GET /ask?q=...&lang=Marathi (lang is optional) */
    @GetMapping("/ask")
    public String ask(@RequestParam String q, @RequestParam(required = false) String lang) {
        return chat.prompt()
                .user(q)
                .advisors(a -> { if (lang != null) a.param(LanguageAdvisor.LANGUAGE, lang); })
                .call()
                .content();
    }

    /** GET /meter: how many model calls, and how many tokens, since the app started. */
    @GetMapping("/meter")
    public Map<String, Long> meter() {
        return Map.of("calls", usage.calls(), "tokens", usage.tokens());
    }
}
