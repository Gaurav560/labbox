package com.setu;

import java.util.List;
import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import dev.langchain4j.guardrail.InputGuardrailException;
import dev.langchain4j.rag.content.Content;
import dev.langchain4j.service.Result;

/** Setu's web API, with sources, a usage page and a polite refusal. */
@RestController
public class SetuController {

    public record ChatRequest(String passenger, String message) {
    }

    /** The answer, and the rule-book files it came from (empty when no rule was needed). */
    public record ChatReply(String passenger, String answer, List<String> sources) {
    }

    private final SetuAssistant setu;
    private final UsageLog usage;

    public SetuController(SetuAssistant setu, UsageLog usage) {
        this.setu = setu;
        this.usage = usage;
    }

    @PostMapping("/chat")
    public ChatReply chat(@RequestBody ChatRequest request) {
        Result<String> result = setu.chat(request.passenger(), request.message());
        List<String> sources = result.sources().stream()
                .map(Content::textSegment)
                .map(segment -> segment.metadata().getString("file_name"))
                .distinct()
                .toList();
        return new ChatReply(request.passenger(), result.content(), sources);
    }

    @GetMapping("/usage")
    public Map<String, Integer> usage() {
        return Map.of("calls", usage.calls(), "inputTokens", usage.inputTokens(), "outputTokens", usage.outputTokens());
    }

    /** The input guardrail stopped the question: say why, and never call the model. */
    @ExceptionHandler(InputGuardrailException.class)
    public ResponseEntity<Map<String, String>> refused(InputGuardrailException e) {
        return ResponseEntity.badRequest().body(Map.of("error", QuestionLimit.TOO_LONG));
    }
}
