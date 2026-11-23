package com.setu.check;

import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Assistant;
import com.setu.Eval;
import com.setu.Models;
import com.setu.UsageLog;

import dev.langchain4j.service.AiServices;

class Ch26Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    @Test
    void usageListener() {
        R.task("usage_listener", () -> {
            UsageLog log = new UsageLog();
            Assistant setu = AiServices.create(Assistant.class, Models.chatModel(FAKE.baseUrl(), "k", log));
            FAKE.reset();
            setu.chat("Hello");
            setu.chat("When does the Ghat Express leave?");
            // The fake model reports 42 tokens in and 8 out for every call.
            String got = log.calls() + " calls, " + log.inputTokens() + " in, " + log.outputTokens() + " out";
            if (log.calls() != 2) {
                R.fail("usage_listener", "Two answers came back, so onResponse ran twice: add 1 to calls each time.", "2 calls, 84 in, 16 out", got);
                return;
            }
            if (log.inputTokens() != 84 || log.outputTokens() != 16) {
                R.fail("usage_listener", "Add each response's tokens: context.chatResponse().metadata().tokenUsage().inputTokenCount() to inputTokens, and outputTokenCount() to outputTokens.",
                        "2 calls, 84 in, 16 out", got);
                return;
            }
            R.pass("usage_listener", "Every call counted, without touching Setu's code: a listener sees the model's traffic from the side.");
        });
    }

    @Test
    void goldenEval() {
        R.task("golden_eval", () -> {
            List<Eval.Golden> golden = List.of(new Eval.Golden("a", "07:15"), new Eval.Golden("b", "Free"),
                    new Eval.Golden("c", "420"), new Eval.Golden("d", "don't know"));
            Assistant fake = q -> switch (q) {
                case "a" -> "It leaves at 07:15.";
                case "b" -> "Children under 5 travel FREE.";
                case "c" -> "The fare is Rs 400.";
                default -> "I don't know, please ask the station office.";
            };
            double got = Eval.passRate(fake, golden);
            if (Math.abs(got - 0.75) > 1e-9) {
                String hint = Math.abs(got - 0.5) < 1e-9
                        ? "\"Children under 5 travel FREE.\" should pass for \"Free\": lower-case both texts before contains(...)."
                        : "Ask every question, count the answers that contain mustContain (ignoring capitals), and return passed / size as a double.";
                R.fail("golden_eval", "Three of these four answers are right. " + hint, "0.75", String.valueOf(got));
                return;
            }
            R.pass("golden_eval", "A number for quality: change the prompt or the model, run the golden set, and see if it went up or down.");
        });
    }
}
