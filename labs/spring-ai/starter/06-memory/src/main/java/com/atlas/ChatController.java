package com.atlas;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.session.SessionService;
import org.springframework.ai.session.advisor.SessionAdvisors;
import org.springframework.ai.session.compaction.TurnCountTrigger;
import org.springframework.ai.session.compaction.WindowCompactionStrategy;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** A conversation with Atlas: every visitor has their own session, kept by their visitor id. */
@RestController
public class ChatController {

    private final ChatClient chat;
    private final SessionService sessions;

    public ChatController(ChatClient.Builder builder, SessionService sessions) {
        this.sessions = sessions;
        this.chat = builder
                .defaultSystem("""
            You are Atlas, the friendly visitor guide of the Deccan Science Museum in Pune.
            Answer in at most three short sentences, in plain, simple words.
            You may answer questions about the museum, its exhibits, and any science topic.
            For anything else, say kindly that you are the museum's guide.
            Never invent opening hours, prices or exhibits: if you do not know, say so.
            """)
                // TODO (task session_memory): add the session advisors, built on the session service.
                // TODO (task memory_window): once a conversation passes 8 turns, keep only its last 4.
                .build();
    }

    /** GET /chat?visitor=ria&q=... one message in this visitor's conversation. */
    @GetMapping("/chat")
    public String chat(@RequestParam String visitor, @RequestParam String q) {
        // TODO (task session_memory): run this call in the visitor's own session.
        return chat.prompt()
                .user(q)
                .call()
                .content();
    }

    /** DELETE /chat/ria: forget this visitor's conversation (for example when they leave the screen). */
    @DeleteMapping("/chat/{visitor}")
    public void forget(@PathVariable String visitor) {
        sessions.delete(visitor);
    }
}
