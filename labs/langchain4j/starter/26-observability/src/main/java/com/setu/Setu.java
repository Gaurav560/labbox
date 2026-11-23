package com.setu;

import dev.langchain4j.service.AiServices;

/** Chapter 26: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) {
        UsageLog log = new UsageLog();
        Assistant setu = AiServices.create(Assistant.class,
                Models.chatModel(System.getenv("OPENAI_BASE_URL"), System.getenv("OPENAI_API_KEY"), log));
        double rate = Eval.passRate(setu, Eval.GOLDEN);
        System.out.printf("golden set: %.0f%% of %d questions passed%n", rate * 100, Eval.GOLDEN.size());
        System.out.printf("usage: %d calls, %d tokens in, %d tokens out, $%.6f%n", log.calls(), log.inputTokens(),
                log.outputTokens(), log.inputTokens() * 0.15 / 1e6 + log.outputTokens() * 0.60 / 1e6);
    }
}
