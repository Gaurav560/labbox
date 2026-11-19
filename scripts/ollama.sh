#!/usr/bin/env bash
# Runs Ollama (free, local models) for the LLM gateway: a Docker container listening on localhost only,
# with the small models the default model aliases use. Safe to run again; it skips what is there.
set -euo pipefail
NAME=labbox-ollama
MODELS=(qwen2.5:0.5b qwen2.5:1.5b nomic-embed-text)

if ! docker ps -a --format '{{.Names}}' | grep -qx "$NAME"; then
  docker run -d --name "$NAME" --restart unless-stopped \
    -p 127.0.0.1:11434:11434 -v labbox-ollama:/root/.ollama ollama/ollama:0.12.6
elif [ "$(docker inspect -f '{{.State.Running}}' "$NAME")" != "true" ]; then
  docker start "$NAME"
fi
for _ in $(seq 1 60); do curl -s -o /dev/null localhost:11434/api/version && break; sleep 1; done
for m in "${MODELS[@]}"; do
  docker exec "$NAME" ollama pull "$m"
done
docker exec "$NAME" ollama list
