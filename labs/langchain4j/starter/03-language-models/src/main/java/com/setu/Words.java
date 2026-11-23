package com.setu;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;

/** Text to words: the first step of every language program, old and new. */
public final class Words {

    private Words() {
    }

    /** The words of a text, in lower case: anything that is not a letter or a digit separates words. */
    public static List<String> split(String text) {
        List<String> out = new ArrayList<>();
        for (String w : text.toLowerCase(Locale.ROOT).split("[^\\p{L}\\p{N}]+")) {
            if (!w.isEmpty()) {
                out.add(w);
            }
        }
        return out;
    }

    // TODO (task count_words): how often each word of the text appears (use split above), A to Z.
    public static Map<String, Integer> count(String text) {
        return new TreeMap<>();
    }
}
