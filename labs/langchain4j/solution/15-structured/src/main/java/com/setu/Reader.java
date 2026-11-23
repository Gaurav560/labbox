package com.setu;

import dev.langchain4j.service.UserMessage;

/** Reads passengers' messages and returns Java objects instead of text. */
public interface Reader {

    @UserMessage("Today is 2026-11-23. Read this booking message and extract the trip: {{it}}")
    TripRequest trip(String message);

    @UserMessage("Which team should handle this passenger message? {{it}}")
    Topic topic(String message);
}
