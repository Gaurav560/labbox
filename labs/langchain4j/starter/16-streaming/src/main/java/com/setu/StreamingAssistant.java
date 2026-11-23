package com.setu;

import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.TokenStream;

/** Setu as an AI Service whose answers stream. */
public interface StreamingAssistant {

    @SystemMessage(fromResource = "setu-system.txt")
    TokenStream chat(String question);
}
