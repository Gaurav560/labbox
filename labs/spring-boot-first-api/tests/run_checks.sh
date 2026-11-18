#!/usr/bin/env bash
# Hidden checks: build offline, start the app, call it with curl. Results are built with jq.
set -u
cd /check/workspace
report() { jq -cn --arg t "$1" --argjson p "$2" --arg m "$3" --arg e "${4:-}" --arg a "${5:-}" \
  '{task: $t, passed: $p, message: $m} + (if $e == "" then {} else {expected: $e, actual: $a} end)' | sed 's/^/@@RESULT /'; }

if ! mvn -o -q -B package -DskipTests > /tmp/build.log 2>&1; then
  echo "Build failed:"; tail -40 /tmp/build.log
  for t in hello merchants; do report "$t" false "Your project does not build. See Output for the compiler message."; done
  exit 0
fi
java -Xmx384m -jar target/merchant-api.jar --server.port=8080 > /tmp/app.log 2>&1 &
for _ in $(seq 1 90); do curl -s -o /dev/null http://127.0.0.1:8080/ && break; sleep 1; done
if ! curl -s -o /dev/null http://127.0.0.1:8080/; then
  echo "App did not start:"; tail -40 /tmp/app.log
  for t in hello merchants; do report "$t" false "The app did not start. See Output."; done
  exit 0
fi

code=$(curl -s -o /tmp/hello -w '%{http_code}' http://127.0.0.1:8080/hello); got=$(cat /tmp/hello)
if [ "$code" = 200 ] && [ "$got" = "Hello from PaySetu!" ]; then report hello true ok
elif [ "$code" = 404 ]; then report hello false "GET /hello returned 404: there is no /hello mapping yet." "200" "404"
else report hello false "GET /hello returned the wrong text." "Hello from PaySetu!" "$code $got"; fi

want='["Annapurna Mess","Chai Point","Kirana King"]'
code=$(curl -s -o /tmp/merchants -w '%{http_code}' http://127.0.0.1:8080/merchants)
got=$(jq -c . /tmp/merchants 2>/dev/null || cat /tmp/merchants)
if [ "$code" = 200 ] && [ "$got" = "$want" ]; then report merchants true ok
elif [ "$code" = 404 ]; then report merchants false "GET /merchants returned 404: there is no /merchants mapping yet." "200" "404"
else report merchants false "GET /merchants should return the names A to Z as a JSON array." "$want" "$code $got"; fi
