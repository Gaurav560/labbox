package com.setu;

import dev.langchain4j.service.MemoryId;
import dev.langchain4j.service.Result;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.guardrail.InputGuardrails;
import dev.langchain4j.service.guardrail.OutputGuardrails;
import dev.langchain4j.service.spring.AiService;

/**
 * Setu, complete. The starter finds and wires every piece by itself: the chat model (with the UsageLog listener), the
 * chat memory provider, the RailTools tools and the rules retriever. The guardrails are named here.
 */
@AiService
@InputGuardrails(QuestionLimit.class)
@OutputGuardrails(NoPhoneNumbers.class)
public interface SetuAssistant {

    /** Result carries the answer and the pieces of the rule book it used. */
    @SystemMessage(fromResource = "setu-system.txt")
    Result<String> chat(@MemoryId String passenger, @UserMessage String message);
}
