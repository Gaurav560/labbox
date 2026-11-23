package com.setu.check;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Bill;

import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.openai.OpenAiChatModel;

class Ch12Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    @Test
    void tokenUsage() {
        R.task("token_usage", () -> {
            FAKE.reset();
            ChatModel model = OpenAiChatModel.builder().baseUrl(FAKE.baseUrl()).apiKey("k").modelName("ai-chat").build();
            ChatResponse r = model.chat(UserMessage.from("Hi"));
            Bill.Usage u = Bill.usage(r);
            if (u == null || u.inputTokens() != 42 || u.outputTokens() != 8) {
                R.fail("token_usage", "The server reported 42 tokens in and 8 out. Read response.metadata().tokenUsage(), then inputTokenCount() and outputTokenCount().",
                        "Usage[inputTokens=42, outputTokens=8]", String.valueOf(u));
                return;
            }
            R.pass("token_usage", "Every answer carries its own receipt. Log it, and you always know what Setu costs.");
        });
    }

    @Test
    void answerCost() {
        R.task("answer_cost", () -> {
            double[][] cases = {{1_000_000, 0, 0.15}, {0, 1_000_000, 0.60}, {180, 60, 0.000063}, {0, 0, 0}};
            for (double[] c : cases) {
                double got = Bill.dollars(new Bill.Usage((int) c[0], (int) c[1]));
                if (Math.abs(got - c[2]) > 1e-12) {
                    String hint = c[1] == 1_000_000 && Math.abs(got - 0.15) < 1e-12
                            ? "Output tokens have their own price: OUTPUT_PER_MILLION."
                            : "Input tokens times INPUT_PER_MILLION, plus output tokens times OUTPUT_PER_MILLION, all divided by 1,000,000 (use doubles, not int division).";
                    R.fail("answer_cost", "dollars(" + (int) c[0] + " in, " + (int) c[1] + " out) is wrong. " + hint, String.valueOf(c[2]), String.valueOf(got));
                    return;
                }
            }
            R.pass("answer_cost", "Output tokens cost four times input tokens. Short answers are the cheapest optimisation there is.");
        });
    }
}
