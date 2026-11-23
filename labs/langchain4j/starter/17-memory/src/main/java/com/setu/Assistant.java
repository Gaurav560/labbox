package com.setu;

import dev.langchain4j.service.SystemMessage;

/** Setu, described as a Java interface. LangChain4j writes the implementation. */
public interface Assistant {

    @SystemMessage(fromResource = "setu-system.txt")
    String chat(String question);
}
