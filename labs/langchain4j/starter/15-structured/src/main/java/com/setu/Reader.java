package com.setu;

import dev.langchain4j.service.UserMessage;

/** Reads passengers' messages and returns Java objects instead of text. */
public interface Reader {

    // TODO (task extract_trip): make this method return a TripRequest instead of a String.
    //   Keep the @UserMessage; LangChain4j sends TripRequest's JSON schema and parses the answer into the record.
    @UserMessage("Today is 2026-11-23. Read this booking message and extract the trip: {{it}}")
    String trip(String message);

    // TODO (task classify_topic): add a method Topic topic(String message), annotated with
    //   @UserMessage("Which team should handle this passenger message? {{it}}")
}
