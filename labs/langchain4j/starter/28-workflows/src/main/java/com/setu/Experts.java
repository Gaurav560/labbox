package com.setu;

import dev.langchain4j.agentic.Agent;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;

/** Three desks, each a specialist agent. Each writes its reply to the scope as "reply". */
public final class Experts {

    private Experts() {
    }

    public interface RefundDesk {
        @SystemMessage(fromResource = "setu-system.txt")
        @UserMessage("You handle refunds. Cancelled 24 hours or more before departure: full refund; less: half; refunds take"
                + " 5 working days. Answer this passenger in two sentences: {{message}}")
        @Agent("Answers refund questions")
        String answer(@V("message") String message);
    }

    public interface TimetableDesk {
        @SystemMessage(fromResource = "setu-system.txt")
        @UserMessage("You handle timetable questions, using only the facts. Answer this passenger in two sentences: {{message}}")
        @Agent("Answers timetable questions")
        String answer(@V("message") String message);
    }

    public interface GeneralDesk {
        @SystemMessage(fromResource = "setu-system.txt")
        @UserMessage("Apologise once, say the right team will reply within a day, in two sentences: {{message}}")
        @Agent("Answers everything else")
        String answer(@V("message") String message);
    }
}
