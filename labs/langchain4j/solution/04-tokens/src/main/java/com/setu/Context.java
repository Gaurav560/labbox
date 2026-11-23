package com.setu;

import java.util.ArrayList;
import java.util.List;

/** A model can only read so many tokens at once: its context window. Chat apps keep the newest messages that fit. */
public final class Context {

    private Context() {
    }

    /** The newest messages that fit in budget tokens together, oldest first. */
    public static List<String> fit(List<String> messages, int budget) {
        List<String> kept = new ArrayList<>();
        int used = 0;
        for (int i = messages.size() - 1; i >= 0; i--) {
            int tokens = Tokens.count(messages.get(i));
            if (used + tokens > budget) {
                break;
            }
            used += tokens;
            kept.add(0, messages.get(i));
        }
        return kept;
    }
}
