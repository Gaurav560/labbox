package com.atlas;

import java.util.List;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.ChatClientResponse;
import org.springframework.ai.chat.client.advisor.vectorstore.QuestionAnswerAdvisor;
import org.springframework.ai.document.Document;
import org.springframework.ai.session.SessionService;
import org.springframework.ai.session.advisor.SessionAdvisors;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

/** The lobby screen's API: one message in a visitor's conversation, answered with sources. */
@RestController
public class LiveController {

    public record Message(String visitor, String text) {}

    public record Reply(String answer, List<String> sources) {}

    private final ChatClient atlas;
    private final SessionService sessions;

    public LiveController(ChatClient atlas, SessionService sessions) {
        this.atlas = atlas;
        this.sessions = sessions;
    }

    /** POST /chat {"visitor": "ria", "text": "..."} */
    @PostMapping("/chat")
    public Reply chat(@RequestBody Message message) {
        ChatClientResponse response = atlas.prompt()
                .user(message.text())
                .advisors(SessionAdvisors.session(message.visitor()))
                .call()
                .chatClientResponse();
        @SuppressWarnings("unchecked")
        List<Document> used = (List<Document>) response.context().get(QuestionAnswerAdvisor.RETRIEVED_DOCUMENTS);
        List<String> sources = used == null ? List.of()
                : used.stream().map(d -> (String) d.getMetadata().get("file")).distinct().toList();
        return new Reply(response.chatResponse().getResult().getOutput().getText(), sources);
    }

    /** DELETE /chat/ria when the visitor leaves the screen. */
    @DeleteMapping("/chat/{visitor}")
    public void forget(@PathVariable String visitor) {
        sessions.delete(visitor);
    }
}
