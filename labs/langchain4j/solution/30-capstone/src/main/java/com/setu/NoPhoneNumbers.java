package com.setu;

import java.util.regex.Pattern;

import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.guardrail.OutputGuardrail;
import dev.langchain4j.guardrail.OutputGuardrailResult;

/** Checked after the model answers: Setu never shows a mobile number, whoever typed it. */
public class NoPhoneNumbers implements OutputGuardrail {

    /** An Indian mobile number: 10 digits starting 6 to 9, maybe written as 5 + 5 or with +91. */
    public static final Pattern MOBILE = Pattern.compile("(?<!\\d)(\\+91[ -]?)?[6-9]\\d{4}[ -]?\\d{5}(?!\\d)");
    public static final String REMOVED = "[number removed]";

    @Override
    public OutputGuardrailResult validate(AiMessage responseFromLLM) {
        String text = responseFromLLM.text();
        if (text != null && MOBILE.matcher(text).find()) {
            return successWith(MOBILE.matcher(text).replaceAll(REMOVED));
        }
        return success();
    }
}
