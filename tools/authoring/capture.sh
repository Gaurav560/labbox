#!/usr/bin/env bash
# A capture machine: the lab's real image, running the solution, so every output quoted in a lesson is real.
#
#   tools/authoring/capture.sh start <lab> <scratch-dir> [token-file]   copy solution/ to <scratch-dir>/ws, start "labcap"
#   tools/authoring/capture.sh run <folder> 'cmd' ['cmd' ...]           run each as the learner, print "$ cmd" and output
#   tools/authoring/capture.sh app <folder> [port]                      start a chapter's app (Maven, in the background)
#   tools/authoring/capture.sh stop                                     remove the machine
#
# With a token file (from author_token.py) the machine reaches the LLM gateway at the Docker bridge address,
# like a real AI lab; without one it has no AI. Edit files in <scratch-dir>/ws to show a wrong version, run
# it, then put the solution back. Paste outputs into lessons as they are (trim only, and say so with "...").
# See COURSE_PRODUCTION.md, "Capturing real output".
set -euo pipefail
NAME=labcap
ROOT=$(cd "$(dirname "$0")/../.." && pwd)

case "${1:-}" in
  start)
    lab=$2; dir=$3; token=${4:-}
    image=$(grep -m1 '^image:' "$ROOT/labs/$lab/lab.yaml" | awk '{print $2}')
    mkdir -p "$dir/ws"; rm -rf "${dir:?}/ws/"*; cp -r "$ROOT/labs/$lab/solution/." "$dir/ws/"
    docker rm -f $NAME >/dev/null 2>&1 || true
    env=()
    if [ -n "$token" ]; then
      env=(-e OPENAI_BASE_URL=http://172.17.0.1:9000/llm/v1 -e "OPENAI_API_KEY=$(cat "$token")"
           -e LABBOX_GATEWAY=http://172.17.0.1:9000)
    fi
    docker run -d --name $NAME --network bridge --init --hostname "$lab" "${env[@]}" \
      -v "$dir/ws:/workspace" "$image" sleep infinity >/dev/null
    echo "started $NAME from $image"
    ;;
  run)
    folder=$2; shift 2
    for c in "$@"; do
      echo "\$ $c"
      docker exec -u 1000 -w "/workspace/$folder" -e HOME=/home/learner $NAME bash -c "$c" 2>&1 || true
    done
    ;;
  app)
    folder=$2; port=${3:-8080}
    docker exec $NAME bash -c 'pkill -f "[s]pring-boot:run" || true; sleep 1'
    docker exec -d -u 1000 -w "/workspace/$folder" -e HOME=/home/learner $NAME \
      bash -c 'mvn -q -o spring-boot:run > /tmp/app.log 2>&1'
    for _ in $(seq 120); do
      docker exec $NAME bash -c "curl -s -o /dev/null localhost:$port/" && break
      sleep 1
    done
    docker exec $NAME tail -3 /tmp/app.log
    ;;
  stop)
    docker rm -f $NAME >/dev/null && echo "removed $NAME"
    ;;
  *)
    sed -n 2,13p "$0"; exit 2
    ;;
esac
