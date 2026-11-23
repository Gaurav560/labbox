package com.setu.check;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;

import com.setu.Bigram;
import com.setu.Words;

class Ch03Check {

    @Test
    void countWords() {
        R.task("count_words", () -> {
            Map<String, Integer> got = Words.count("The Ghat Express, the GHAT express! Platform 2.");
            String want = "{2=1, express=2, ghat=2, platform=1, the=2}";
            if (got == null || !want.equals(new java.util.TreeMap<>(got).toString())) {
                R.fail("count_words", "Words.count is not right. Split the text with Words.split (it lower-cases and drops punctuation), then add 1 for each word.",
                        want, String.valueOf(got));
                return;
            }
            if (!new ArrayList<>(got.keySet()).equals(new ArrayList<>(new java.util.TreeMap<>(got).keySet()))) {
                R.fail("count_words", "The counts are right but not A to Z: keep them in a TreeMap.", want, got.toString());
                return;
            }
            if (!Words.count("").isEmpty()) {
                R.fail("count_words", "An empty text has no words: Words.count(\"\") should be empty.", "{}", Words.count("").toString());
                return;
            }
            R.pass("count_words", "A bag of words: how search engines and spam filters saw text for decades.");
        });
    }

    @Test
    void nextWord() {
        R.task("next_word", () -> {
            Bigram m = new Bigram();
            m.train(List.of("the ghat express is late", "the ghat express is on time", "the konkan breeze is late",
                    "a train is early"));
            String[][] cases = {{"the", "ghat"}, {"ghat", "express"}, {"is", "late"}, {"a", "train"}};
            for (String[] c : cases) {
                String got = m.next(c[0]);
                if (!c[1].equals(got)) {
                    R.fail("next_word", "After '" + c[0] + "' the most frequent next word is '" + c[1] + "'. Look up follows.get(word) and pick the entry with the biggest count.",
                            c[1], String.valueOf(got));
                    return;
                }
            }
            Bigram tie = new Bigram();
            tie.train(List.of("to pune", "to karjat", "to lonavala"));
            if (!"karjat".equals(tie.next("to"))) {
                R.fail("next_word", "'to' was followed by pune, karjat and lonavala once each: on a tie, return the first A to Z.", "karjat", String.valueOf(tie.next("to")));
                return;
            }
            if (m.next("platform") != null || m.next("late") != null) {
                R.fail("next_word", "A word the model never saw, or never saw followed by anything, has no next word: return null.", "null",
                        m.next("platform") + " / " + m.next("late"));
                return;
            }
            R.pass("next_word", "Count, then predict the likeliest next word: an LLM does the same job, with far better counts.");
        });
    }
}
