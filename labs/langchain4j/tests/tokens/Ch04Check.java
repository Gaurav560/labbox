package com.setu.check;

import java.util.List;

import org.junit.jupiter.api.Test;

import com.setu.Context;
import com.setu.Tokens;

import dev.langchain4j.model.openai.OpenAiTokenCountEstimator;

class Ch04Check {

    static final OpenAiTokenCountEstimator E = new OpenAiTokenCountEstimator("gpt-4o-mini");

    @Test
    void countTokens() {
        R.task("count_tokens", () -> {
            for (String t : new String[] {"Lonavala", "When does the Ghat Express leave Pune?", "पुणे ते लोणावळा", "🚆"}) {
                int want = E.estimateTokenCountInText(t);
                int got = Tokens.count(t);
                if (got != want) {
                    R.fail("count_tokens", "Tokens.count(\"" + t + "\") is not what gpt-4o-mini's tokenizer says. Return ESTIMATOR.estimateTokenCountInText(text).",
                            String.valueOf(want), String.valueOf(got));
                    return;
                }
            }
            R.pass("count_tokens", "Now you can count what a model reads, and what it bills: tokens, not words.");
        });
    }

    @Test
    void fitWindow() {
        R.task("fit_window", () -> {
            if (Tokens.count("Lonavala") == 0) {
                R.fail("fit_window", "Context.fit counts tokens with Tokens.count, which still returns 0: finish the task before this one (count_tokens) first.");
                return;
            }
            List<String> chat = List.of(
                    "Passenger: Hello! I am travelling with my grandmother next Sunday.",
                    "Setu: Hello! How can I help you plan the trip?",
                    "Passenger: We want the morning train from Pune to Lonavala.",
                    "Setu: The Ghat Express leaves Pune at 7:15 and reaches Lonavala at 8:40.",
                    "Passenger: Can she get a lower berth?");
            int last = E.estimateTokenCountInText(chat.get(4));
            int last2 = last + E.estimateTokenCountInText(chat.get(3));
            int all = 0;
            for (String m : chat) all += E.estimateTokenCountInText(m);
            Object[][] cases = {{last2, chat.subList(3, 5)}, {last2 + 1, chat.subList(3, 5)}, {all, chat}, {last - 1, List.of()}};
            for (Object[] c : cases) {
                List<String> got = Context.fit(chat, (int) c[0]);
                if (!c[1].equals(got)) {
                    String hint = ((List<?>) c[1]).isEmpty()
                            ? "Even the newest message does not fit in " + c[0] + " tokens, so nothing is kept."
                            : got != null && got.size() == ((List<?>) c[1]).size() && !got.equals(c[1])
                                    ? "The right messages, in the wrong order: return them oldest first."
                                    : "Start from the newest message, add messages while the total stays within the budget, and stop at the first that does not fit.";
                    R.fail("fit_window", "Context.fit(chat, " + c[0] + ") kept the wrong messages. " + hint, String.valueOf(c[1]), String.valueOf(got));
                    return;
                }
            }
            // An older, shorter message must not jump the queue: the window is the most recent part of the chat.
            List<String> uneven = List.of("ok", "Setu: The Ghat Express leaves Pune at 7:15 and reaches Lonavala at 8:40.", "Thanks!");
            int budget = E.estimateTokenCountInText("Thanks!") + E.estimateTokenCountInText("ok");
            List<String> got = Context.fit(uneven, budget);
            if (!List.of("Thanks!").equals(got)) {
                R.fail("fit_window", "Stop at the first message that does not fit: an older message must not be kept when a newer one was dropped.",
                        "[Thanks!]", String.valueOf(got));
                return;
            }
            R.pass("fit_window", "That is how a chat app fits a long conversation into a model's context window: the newest part, in order.");
        });
    }
}
