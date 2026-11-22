package com.atlas;

import org.springframework.ai.chat.client.ChatClientRequest;
import org.springframework.ai.chat.client.ChatClientResponse;
import org.springframework.ai.chat.client.advisor.api.AdvisorChain;
import org.springframework.ai.chat.client.advisor.api.BaseAdvisor;

/** Answers in the visitor's language, when the request says which one. */
public class LanguageAdvisor implements BaseAdvisor {

    /** The advisor parameter that carries the language, set per request. */
    public static final String LANGUAGE = "language";

    @Override
    public ChatClientRequest before(ChatClientRequest request, AdvisorChain chain) {
        // TODO (task language_advisor): if the request's context has a language, add "Answer in LANGUAGE." to the system message.
        return request;
    }

    @Override
    public ChatClientResponse after(ChatClientResponse response, AdvisorChain chain) {
        return response;
    }

    @Override
    public int getOrder() {
        return 0;
    }
}
