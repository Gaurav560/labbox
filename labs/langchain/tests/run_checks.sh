#!/usr/bin/env bash
# Hidden checks for LangChain. Each chapter's checks are pytest files, run inside a temporary copy of that
# chapter's folder with a fake OpenAI server (no network, no cost). They print one @@RESULT line per task and never
# fail the run, so every task gets a result. LABBOX_CHAPTER (set by LabBox) limits the run to one chapter.
set -u
W=/check/workspace
T=/check/tests

# chapter id | project folder | tasks
CHAPTERS="
ai-basics|01-ai-basics|rule_reply learn_threshold
tokens|02-tokens|count_tokens fit_window
embeddings|03-embeddings|cosine closest_question
transformers|04-transformers|softmax_temperature attention_weights
raw-http|05-raw-http|send_request read_answer
openai-sdk|06-openai-sdk|sdk_client sdk_ask
first-app|07-first-app|chat_model system_message
parameters|08-parameters|steady_model stream_tokens
hallucinations|09-hallucinations|honest_prompt answer_cost
agent-loop|10-agent-loop|run_tool_call agent_loop
create-agent|11-create-agent|first_agent tools_used
tools|12-tools|loan_tool member_tool
structured|13-structured|extract_booking booking_agent
images|14-images|image_message leaf_report
memory|15-memory|memory_agent thread_per_member
streaming|16-streaming|stream_steps stream_answer_text
documents|17-documents|load_rules split_rules
vector-stores|18-vector-stores|store_chunks search_threshold
rag|19-rag|rules_tool rag_agent
retrieval-quality|20-retrieval-quality|hit_rate titled_chunks
mcp|21-mcp|mcp_server mcp_agent
middleware|22-middleware|tool_errors limits_and_summaries
custom-middleware|23-custom-middleware|member_prompt audit_tools
guardrails|24-guardrails|aadhaar_detector length_guard
human-in-the-loop|25-human-in-the-loop|approval_middleware resume_decision
evals|26-evals|golden_eval judge_answer
capstone|27-capstone|remember_fact chat_endpoint
"

fail_all() { # tasks message
  local m; m=$(printf '%s' "$2" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' ' ')
  for t in $1; do echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"Not yet: $m\"}"; done
}

echo "$CHAPTERS" | while IFS='|' read -r chapter dir tasks; do
  [ -z "$chapter" ] && continue
  [ -n "${LABBOX_CHAPTER:-}" ] && [ "$LABBOX_CHAPTER" != "$chapter" ] && continue
  if [ ! -d "$W/$dir" ]; then fail_all "$tasks" "the folder $dir is missing from your workspace."; continue; fi
  work=/tmp/check/$chapter
  rm -rf "$work"; mkdir -p "$work"
  (cd "$W/$dir" && tar --exclude=__pycache__ --exclude=.venv -cf - .) | (cd "$work" && tar -xf -)
  mkdir -p "$work/_checks"
  cp "$T/common"/*.py "$T/$chapter"/*.py "$work/_checks/"
  log=/tmp/check/$chapter.log
  (cd "$work" && timeout 200 python3 -m pytest -q -s -p no:cacheprovider --rootdir="$work/_checks" "$work/_checks" > "$log" 2>&1)
  results=$(grep -o '@@RESULT .*' "$log")
  printf '%s\n' "$results" | grep -v '^$'
  missing=""
  for t in $tasks; do printf '%s' "$results" | grep -q "\"task\": \"$t\"" || missing="$missing $t"; done
  if [ -n "$missing" ]; then
    why=$(grep -m1 -E "^E +[A-Za-z]+Error|SyntaxError|IndentationError|ModuleNotFoundError" "$log" | sed -E 's/^E +//' | cut -c1-220)
    fail_all "$missing" "the checks could not run your code: ${why:-see Output}."
    echo "---- $chapter: the last lines ----"; tail -20 "$log"
  fi
done
