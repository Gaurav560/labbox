package com.setu;

import dev.langchain4j.agentic.Agent;
import dev.langchain4j.service.V;

/** The whole help desk, as one typed agent: a message in, a reply out. */
public interface DeskWorkflow {

    @Agent
    String handle(@V("message") String message);
}
