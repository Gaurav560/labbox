package com.setu;

import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;

/** A station desk: the same question means different things at different stations. */
public interface StationDesk {

    @SystemMessage(fromResource = "setu-system.txt")
    @UserMessage("A passenger at {{station}} station asks: {{question}}")
    String ask(@V("station") String station, @V("question") String question);
}
