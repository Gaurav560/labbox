package com.setu;

import dev.langchain4j.service.MemoryId;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;

// TODO (task ai_service_bean): annotate this interface with @AiService (dev.langchain4j.service.spring.AiService),
//   so the starter implements it and makes it a Spring bean you can inject.
public interface SetuAssistant {

    @SystemMessage(fromResource = "setu-system.txt")
    String chat(@MemoryId String passenger, @UserMessage String message);
}
