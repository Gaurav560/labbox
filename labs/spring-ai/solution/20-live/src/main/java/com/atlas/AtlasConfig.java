package com.atlas;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.SafeGuardAdvisor;
import org.springframework.ai.chat.client.advisor.vectorstore.QuestionAnswerAdvisor;
import org.springframework.ai.session.SessionService;
import org.springframework.ai.session.advisor.SessionAdvisors;
import org.springframework.ai.session.compaction.TurnCountTrigger;
import org.springframework.ai.session.compaction.WindowCompactionStrategy;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** The whole of Atlas in one ChatClient: everything this course built, working together. */
@Configuration
public class AtlasConfig {

    static final java.util.List<String> PRIVATE_WORDS = java.util.List.of("my address", "my phone number", "my password", "my school is");

    static final String PRIVACY_REPLY = "Please keep personal details like addresses, phone numbers and passwords to yourself. "
            + "I am the museum's guide: ask me about the exhibits!";

    @Bean
    ChatClient atlas(ChatClient.Builder builder, MuseumTools tools, VectorStore store, SessionService sessions) {
        return builder
                .defaultSystem("""
            You are Atlas, the friendly visitor guide of the Deccan Science Museum in Pune.
            Answer in at most three short sentences, in plain, simple words.
            You may answer questions about the museum, its exhibits, and any science topic.
            For anything else, say kindly that you are the museum's guide.
            Never invent opening hours, prices or exhibits: if you do not know, say so.
            Use the tools for dates, opening hours and show times.
            """)
                .defaultTools(tools)
                .defaultAdvisors(SessionAdvisors.builder(sessions)
                        .compaction(new TurnCountTrigger(8), WindowCompactionStrategy.builder().lastTurns(4).build())
                        .build())
                .defaultAdvisors(
                        SafeGuardAdvisor.builder().sensitiveWords(PRIVATE_WORDS).failureResponse(PRIVACY_REPLY).order(0).build(),
                        new QuestionLimitAdvisor(300),
                        QuestionAnswerAdvisor.builder(store)
                                .searchRequest(SearchRequest.builder().topK(3).similarityThreshold(0.35).build())
                                .build())
                .build();
    }
}
