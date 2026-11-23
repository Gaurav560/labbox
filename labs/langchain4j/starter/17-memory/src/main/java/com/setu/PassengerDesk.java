package com.setu;

import dev.langchain4j.service.MemoryId;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;

/** Setu for many passengers at once: each passenger has their own conversation. */
public interface PassengerDesk {

    @SystemMessage(fromResource = "setu-system.txt")
    String chat(@MemoryId String passenger, @UserMessage String message);
}
