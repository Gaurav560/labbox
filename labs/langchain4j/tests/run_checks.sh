#!/usr/bin/env bash
# Hidden checks for LangChain4j. Each chapter's checks are JUnit tests (with a fake model server from chapter 7 on)
# copied into a temporary copy of that chapter's project and run offline with Maven. They print one @@RESULT line
# per task and never fail the build, so every task gets a result. A project that does not compile fails only that
# chapter's tasks. LABBOX_CHAPTER (set by LabBox) limits the run to one chapter.
set -u
W=/check/workspace
T=/check/tests

# chapter id | project folder | tasks
CHAPTERS="
ai-basics|01-ai-basics|rule_reply learn_threshold
neurons|02-neurons|neuron_fire train_neuron
language-models|03-language-models|count_words next_word
tokens|04-tokens|count_tokens fit_window
embeddings|05-embeddings|cosine closest_question
transformers|06-transformers|softmax_temperature attention_weights
raw-http|07-raw-http|send_request read_answer
openai-sdk|08-openai-sdk|sdk_client sdk_ask
first-app|09-first-app|chat_model system_message
parameters|10-parameters|steady_model short_answer
hallucinations|11-hallucinations|honest_prompt grounded_answer
usage|12-usage|token_usage answer_cost
ai-services|13-ai-services|ai_service system_annotation
templates|14-templates|prompt_template template_service
structured|15-structured|extract_trip classify_topic
streaming|16-streaming|stream_tokens token_stream
memory|17-memory|window_memory memory_per_passenger
rest-api|18-rest-api|ai_service_bean chat_endpoint
"

fail_all() { # tasks message
  local m; m=$(printf '%s' "$2" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' ' ')
  for t in $1; do echo "@@RESULT {\"task\": \"$t\", \"passed\": false, \"message\": \"Not yet: $m\"}"; done
}

echo "$CHAPTERS" | while IFS='|' read -r chapter dir tasks; do
  [ -z "$chapter" ] && continue
  [ -n "${LABBOX_CHAPTER:-}" ] && [ "$LABBOX_CHAPTER" != "$chapter" ] && continue
  if [ ! -f "$W/$dir/pom.xml" ]; then fail_all "$tasks" "the project folder $dir is missing from your workspace."; continue; fi
  work=/tmp/check/$chapter
  rm -rf "$work"; mkdir -p "$work"
  (cd "$W/$dir" && tar --exclude=./target -cf - .) | (cd "$work" && tar -xf -)
  dest="$work/src/test/java/com/setu/check"
  mkdir -p "$dest"
  cp "$T/common"/*.java "$T/$chapter"/*.java "$dest/"
  # The fake model server (chapter 7 on) only goes in when the chapter's checks use it.
  if grep -q "FakeOpenAi" "$T/$chapter"/*.java; then cp "$T/fake"/*.java "$dest/"; fi
  log=/tmp/check/$chapter.log
  (cd "$work" && MAVEN_OPTS="-Xmx256m" mvn -o -q -B test -Dsurefire.failIfNoSpecifiedTests=false \
      -Dtest="**/check/*Check" -DargLine="-Xmx512m" > "$log" 2>&1)
  results=$(grep -o '@@RESULT .*' "$log")
  printf '%s\n' "$results" | grep -v '^$'
  missing=""
  for t in $tasks; do printf '%s' "$results" | grep -q "\"task\": \"$t\"" || missing="$missing $t"; done
  if [ -n "$missing" ]; then
    if grep -q "COMPILATION ERROR" "$log"; then
      why=$(grep -m1 -E "\[ERROR\] .*\.java:\[[0-9]+" "$log" | sed -E 's/.*\/src\/(main|test)\/java\///; s/^\[ERROR\] //')
      fail_all "$missing" "the project does not compile: ${why:-see Output}."
    elif grep -q "No qualifying bean of type 'com.setu.SetuAssistant'" "$log"; then
      fail_all "$missing" "the app did not start: Spring found no SetuAssistant bean to give SetuController. Annotate the SetuAssistant interface with @AiService."
    else
      why=$(grep -E "^Caused by: " "$log" | tail -1 | sed -E 's/^Caused by: [A-Za-z0-9_.$]+: //' | cut -c1-220)
      fail_all "$missing" "the check could not run: ${why:-see Output}."
    fi
    echo "---- $chapter: the last lines of the build ----"; tail -25 "$log"
  fi
done
