package com.setu;

import dev.langchain4j.guardrail.InputGuardrail;
import dev.langchain4j.guardrail.InputGuardrailRequest;
import dev.langchain4j.guardrail.InputGuardrailResult;

/** Chapter 25's guard, made safe for RAG: it measures what the passenger typed, not what retrieval added. */
public class QuestionLimit implements InputGuardrail {

    public static final int MAX = 300;
    public static final String TOO_LONG = "That question is too long for me. Please ask it in at most 300 characters.";

    @Override
    public InputGuardrailResult validate(InputGuardrailRequest request) {
        // request.userMessage() is the message after RAG: the question plus the rule-book pieces found for it.
        // userMessageTemplate() is the message as the method received it, before anything was added.
        String question = request.requestParams().userMessageTemplate();
        if (question == null) {
            question = request.userMessage().singleText();
        }
        if (question.length() > MAX) {
            return fatal(TOO_LONG);
        }
        return success();
    }
}
