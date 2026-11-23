package com.setu.check;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Assistant;
import com.setu.NoPhoneNumbers;
import com.setu.QuestionLimit;

import dev.langchain4j.guardrail.InputGuardrailException;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.service.AiServices;

class Ch25Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    static OpenAiChatModel model() {
        return OpenAiChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-chat").build();
    }

    @Test
    void questionLimit() {
        R.task("question_limit", () -> {
            Assistant setu = AiServices.builder(Assistant.class).chatModel(model()).inputGuardrails(new QuestionLimit()).build();
            FAKE.reset();
            String longQuestion = "Please tell me everything about the Konkan Breeze. ".repeat(7);
            try {
                setu.chat(longQuestion);
                R.fail("question_limit", "A " + longQuestion.length() + "-character question went through. In validate(...), return fatal(TOO_LONG) when userMessage.singleText().length() > MAX.");
                return;
            } catch (InputGuardrailException e) {
                if (!e.getMessage().contains(QuestionLimit.TOO_LONG)) {
                    R.fail("question_limit", "The question was stopped, but with another message. Return fatal(TOO_LONG).", QuestionLimit.TOO_LONG, e.getMessage());
                    return;
                }
            }
            if (!FAKE.chatRequests.isEmpty()) {
                R.fail("question_limit", "The long question still reached the model. A fatal input guardrail result stops the call before the model.");
                return;
            }
            String exact = "x".repeat(QuestionLimit.class.getDeclaredField("MAX").getInt(null));
            try {
                setu.chat(exact);
                setu.chat("When does the Ghat Express leave?");
            } catch (InputGuardrailException e) {
                R.fail("question_limit", "A question of exactly 300 characters, or a short one, was refused. Refuse only when the length is more than MAX (>, not >=).");
                return;
            }
            if (FAKE.chatRequests.size() != 2) {
                R.fail("question_limit", "Short questions should reach the model: return success() when the question is not too long.");
                return;
            }
            R.pass("question_limit", "Over 300 characters never reaches the model: refused for free, before a single token is paid for.");
        });
    }

    @Test
    void phoneRedactor() {
        R.task("phone_redactor", () -> {
            Assistant setu = AiServices.builder(Assistant.class).chatModel(model()).outputGuardrails(new NoPhoneNumbers()).build();
            FAKE.reset();
            FAKE.script = b -> FakeOpenAi.Reply.text("Call Ravi on 98220 12345 or +91 98220-12345 today.");
            String got = setu.chat("Ravi's number?");
            String want = "Call Ravi on [number removed] or [number removed] today.";
            if (!want.equals(got)) {
                R.fail("phone_redactor", "Every mobile number in the answer should become [number removed]: return successWith(MOBILE.matcher(text).replaceAll(REMOVED)).", want, got);
                return;
            }
            FAKE.script = b -> FakeOpenAi.Reply.text("The Ratnagiri fare is Rs 420 and the train number is 12345.");
            got = setu.chat("Fare?");
            if (!"The Ratnagiri fare is Rs 420 and the train number is 12345.".equals(got)) {
                R.fail("phone_redactor", "An answer with no mobile number should come back unchanged: return success() when MOBILE finds nothing.",
                        "The Ratnagiri fare is Rs 420 and the train number is 12345.", got);
                return;
            }
            R.pass("phone_redactor", "The model may write a number; the passenger never sees it. The guardrail rewrote the answer, without calling the model again.");
        });
    }
}
