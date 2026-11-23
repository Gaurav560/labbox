package com.setu;

import java.util.Map;

import dev.langchain4j.model.input.PromptTemplate;

/** Prompt templates: the same instructions, with blanks filled in for each case. */
public final class Announcements {

    static final PromptTemplate DELAY = PromptTemplate.from(
            "Write one short, calm station announcement in English and Marathi: the {{train}} to {{destination}} "
                    + "is running {{minutes}} minutes late. Apologise once.");

    private Announcements() {
    }

    /** The template with its blanks filled in. */
    public static String delayPrompt(String train, String destination, int minutes) {
        return DELAY.apply(Map.of("train", train, "destination", destination, "minutes", minutes)).text();
    }
}
