package com.setu;

import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.guardrail.InputGuardrail;
import dev.langchain4j.guardrail.InputGuardrailResult;

/** Checked before the model is called: an over-long question never reaches it, and costs nothing. */
public class QuestionLimit implements InputGuardrail {

    public static final int MAX = 300;
    public static final String TOO_LONG = "That question is too long for me. Please ask it in at most 300 characters.";

    @Override
    public InputGuardrailResult validate(UserMessage userMessage) {
        if (userMessage.singleText().length() > MAX) {
            return fatal(TOO_LONG);
        }
        return success();
    }
}
