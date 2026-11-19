#!/usr/bin/env bash
# Starts two copies of the app, like two servers, on ports 8001 and 8002. The load balancer
# (http://lb:8080) sends each request to one of them. Run it again after every change.
pkill -u "$(id -u)" -f "uvicorn app:app" 2>/dev/null
sleep 0.5
for port in 8001 8002; do
  PORT=$port nohup uvicorn app:app --host 0.0.0.0 --port "$port" > "/tmp/app-$port.log" 2>&1 &
done
for _ in $(seq 1 30); do
  curl -s -o /dev/null localhost:8001/health && curl -s -o /dev/null localhost:8002/health && break
  sleep 0.3
done
echo "Two copies running (8001, 8002). Through the load balancer:"
curl -s -H "X-API-Key: test" http://lb:8080/quote; echo
