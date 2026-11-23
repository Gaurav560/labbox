package com.setu;

import dev.langchain4j.service.MemoryId;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.spring.AiService;

@AiService
public interface SetuAssistant {

    @SystemMessage(fromResource = "setu-system.txt")
    String chat(@MemoryId String passenger, @UserMessage String message);
}
