#!/usr/bin/env bash
# Hidden checks for RAG and vector databases. Each chapter's checks are pytest files, run inside a temporary copy of
# that chapter's folder, offline: the embedding and reranking models are in the image, and the chapters that call a
# model get a fake OpenAI server (no network, no cost). One @@RESULT line per task; the run never fails as a whole.
# LABBOX_CHAPTER (set by LabBox) limits the run to one chapter.
set -u
W=/check/workspace
T=/check/tests

# chapter id | project folder | tasks
CHAPTERS="
why-rag|01-why-rag|keyword_search context_prompt
embeddings|02-embeddings|embed_texts cosine
vector-search|03-vector-search|normalize top_k
chunking|04-chunking|word_chunks section_chunks
ivf|05-ivf|build_lists ivf_search
hnsw|06-hnsw|recall_at_k tune_ef
quantization|07-quantization|quantize_int8 binary_rescore
qdrant|08-qdrant|make_store filtered_search
hybrid|09-hybrid|bm25_scores rrf_fuse
rerank|10-rerank|rerank two_stage
grounded-answers|11-grounded-answers|grounded_prompt refuse_unsure
evaluation|12-evaluation|hit_rate mrr
capstone|13-capstone|search_endpoint ask_endpoint
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
    if grep -q "SyntaxError\|IndentationError" "$log"; then
      fail_all "$missing" "fieldbook.py (or another file) has a syntax error: $(grep -m1 -B2 'Error' "$log" | tr -s ' ' | head -c 300)"
    elif grep -q "ModuleNotFoundError\|ImportError" "$log"; then
      fail_all "$missing" "an import failed: $(grep -m1 'Error:' "$log" | head -c 300)"
    else
      fail_all "$missing" "the check could not run. The last lines it printed: $(tail -5 "$log" | tr -s ' ' | head -c 400)"
    fi
  fi
done
exit 0
