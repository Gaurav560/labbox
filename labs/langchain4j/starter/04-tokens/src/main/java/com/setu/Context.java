package com.setu;

import java.util.ArrayList;
import java.util.List;

/** A model can only read so many tokens at once: its context window. Chat apps keep the newest messages that fit. */
public final class Context {

    private Context() {
    }

    // TODO (task fit_window): keep the newest messages whose tokens (Tokens.count) add up to at most budget.
    //   Walk from the newest (the last) backwards and stop at the first message that does not fit.
    //   Return the kept messages in their original order, oldest first.
    public static List<String> fit(List<String> messages, int budget) {
        return new ArrayList<>(messages);
    }
}
