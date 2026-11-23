package com.setu;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/** A bigram model: it learns which word follows which, then predicts the next word. A language model, in miniature. */
public final class Bigram {

    /** For each word, how often each other word came right after it. */
    final Map<String, Map<String, Integer>> follows = new HashMap<>();

    /** Learn from sentences: count every pair of neighbouring words (use Words.split). */
    public void train(List<String> sentences) {
        for (String sentence : sentences) {
            List<String> words = Words.split(sentence);
            for (int i = 0; i + 1 < words.size(); i++) {
                follows.computeIfAbsent(words.get(i), k -> new TreeMap<>()).merge(words.get(i + 1), 1, Integer::sum);
            }
        }
    }

    /** The most frequent follower of this word (A to Z on a tie), or null if the word was never seen. */
    public String next(String word) {
        Map<String, Integer> after = follows.get(word);
        if (after == null) {
            return null;
        }
        String best = null;
        for (Map.Entry<String, Integer> e : after.entrySet()) {   // a TreeMap: A to Z, so the first wins a tie
            if (best == null || e.getValue() > after.get(best)) {
                best = e.getKey();
            }
        }
        return best;
    }

    /** Generate text: start with a word and keep adding the predicted next one. */
    public String generate(String start, int maxWords) {
        StringBuilder out = new StringBuilder(start);
        String word = start;
        for (int i = 1; i < maxWords; i++) {
            word = next(word);
            if (word == null) {
                break;
            }
            out.append(' ').append(word);
        }
        return out.toString();
    }
}
