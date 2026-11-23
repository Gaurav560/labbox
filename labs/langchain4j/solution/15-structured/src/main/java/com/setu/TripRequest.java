package com.setu;

import dev.langchain4j.model.output.structured.Description;

/** What a passenger wants to book, pulled out of a free-text message. */
public record TripRequest(
        @Description("departure station") String from,
        @Description("arrival station") String to,
        @Description("travel date as YYYY-MM-DD") String date,
        @Description("number of passengers") int passengers) {
}
