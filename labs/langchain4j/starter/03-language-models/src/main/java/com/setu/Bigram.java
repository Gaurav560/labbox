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

    // TODO (task next_word): the word that most often came right after this one, or null if the model never saw
    //   the word. If two words came after it equally often, return the one that comes first A to Z.
    public String next(String word) {
        return null;
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
