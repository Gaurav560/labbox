package com.setu;

import dev.langchain4j.agentic.Agent;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;

/** A reviewer that scores a reply, and an editor that improves it. */
public final class Review {

    private Review() {
    }

    public interface ReplyScorer {
        @UserMessage("Score this reply to a railway passenger from 0.0 to 1.0: 1.0 means at most two sentences, kind,"
                + " clear and with no promises it cannot keep. Reply with only the number. The reply: {{reply}}")
        @Agent("Scores a reply")
        double score(@V("reply") String reply);
    }

    public interface ReplyEditor {
        @UserMessage("Rewrite this reply to a railway passenger: at most two sentences, kind, clear, no promises."
                + " Return only the new reply. The reply: {{reply}}")
        @Agent("Improves a reply")
        String edit(@V("reply") String reply);
    }
}
