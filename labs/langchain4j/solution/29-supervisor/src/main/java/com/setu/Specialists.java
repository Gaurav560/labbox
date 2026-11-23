package com.setu;

import dev.langchain4j.agentic.Agent;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;

/** Small agents with one job each; they use RailTools for facts. The supervisor decides which to call. */
public final class Specialists {

    private Specialists() {
    }

    public interface FareAgent {
        @UserMessage("Use the fare tool to find the fare from Pune to {{destination}} for one adult. Return only the number.")
        @Agent("Finds the fare in rupees from Pune to a station, for one adult")
        int fare(@V("destination") String destination);
    }

    public interface DateAgent {
        @UserMessage("Use the date tool to find the date of the next {{day}}. Return only the date.")
        @Agent("Finds the date of the next given day of the week")
        String date(@V("day") String day);
    }
}
