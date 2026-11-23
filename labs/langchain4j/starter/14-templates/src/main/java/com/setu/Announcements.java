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

    // TODO (task prompt_template): fill DELAY's blanks with apply(Map.of(...)) (keys train, destination, minutes)
    //   and return the resulting prompt's text.
    public static String delayPrompt(String train, String destination, int minutes) {
        return "";
    }
}
