package com.setu;

import dev.langchain4j.agentic.Agent;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;

/** An agent: an AI Service with a name, a description, and an output key in the shared scope. */
public interface TopicClassifier {

    @UserMessage("Which team should handle this passenger message? Answer with one word. Message: {{message}}")
    @Agent("Decides which team should handle a passenger message")
    Topic classify(@V("message") String message);
}
