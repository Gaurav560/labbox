package com.setu;

import dev.langchain4j.service.SystemMessage;

/** A station desk: the same question means different things at different stations. */
public interface StationDesk {

    // TODO (task template_service): turn this method into a template. Annotate it with
    //   @UserMessage("A passenger at {{station}} station asks: {{question}}")
    //   and name each parameter for the template with @V("station") and @V("question").
    @SystemMessage(fromResource = "setu-system.txt")
    String ask(String station, String question);
}
