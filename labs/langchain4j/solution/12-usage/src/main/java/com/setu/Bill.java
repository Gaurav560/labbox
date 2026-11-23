package com.setu;

import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.output.TokenUsage;

/** Every answer comes with a receipt: how many tokens went in and came out. */
public final class Bill {

    /** gpt-4o-mini's price, in US dollars per million tokens. */
    static final double INPUT_PER_MILLION = 0.15;
    static final double OUTPUT_PER_MILLION = 0.60;

    /** What one answer used. */
    public record Usage(int inputTokens, int outputTokens) {
    }

    private Bill() {
    }

    /** Tokens in and out, as reported by the model's server. */
    public static Usage usage(ChatResponse response) {
        TokenUsage tokens = response.metadata().tokenUsage();
        return new Usage(tokens.inputTokenCount(), tokens.outputTokenCount());
    }

    /** Input and output tokens, each at its own price. */
    public static double dollars(Usage usage) {
        return usage.inputTokens() * INPUT_PER_MILLION / 1_000_000
                + usage.outputTokens() * OUTPUT_PER_MILLION / 1_000_000;
    }
}
