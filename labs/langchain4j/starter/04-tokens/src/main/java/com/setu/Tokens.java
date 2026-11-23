package com.setu;

import dev.langchain4j.model.openai.OpenAiTokenCountEstimator;

/** Models read tokens, not words. This uses the same tokenizer as gpt-4o-mini, offline. */
public final class Tokens {

    static final OpenAiTokenCountEstimator ESTIMATOR = new OpenAiTokenCountEstimator("gpt-4o-mini");

    private Tokens() {
    }

    // TODO (task count_tokens): how many tokens gpt-4o-mini sees in this text (ask ESTIMATOR).
    public static int count(String text) {
        return 0;
    }
}
