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

    // TODO (task token_usage): read the TokenUsage from the response's metadata and return its input and output
    //   token counts as a Usage.
    public static Usage usage(ChatResponse response) {
        return new Usage(0, 0);
    }

    // TODO (task answer_cost): what this usage cost in US dollars: input tokens at INPUT_PER_MILLION per million,
    //   plus output tokens at OUTPUT_PER_MILLION per million.
    public static double dollars(Usage usage) {
        return 0;
    }
}
