package com.setu;

import dev.langchain4j.agentic.Agent;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;

/** Writes the first reply, knowing which team the message went to. */
public interface ReplyWriter {

    @SystemMessage(fromResource = "setu-system.txt")
    @UserMessage("A passenger wrote: {{message}}\nIt has been sent to the {{topic}} team. Write a short, kind first reply"
            + " that says which team will handle it. Two sentences at most.")
    @Agent("Writes a short first reply to a passenger")
    String write(@V("message") String message, @V("topic") Topic topic);
}
