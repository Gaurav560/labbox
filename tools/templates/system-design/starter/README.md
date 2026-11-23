# Book Point: quotes API

- `app.py`: the API. Two copies run at once (`bash run.sh`), and a real nginx load balancer at
  `http://lb:8080` sends each request to one of them, like two servers in production.
- Redis is at `redis` (`redis-cli` is already pointed at it).
- Try it: `curl -H "X-API-Key: alice" http://lb:8080/quote`
- Logs: `/tmp/app-8001.log` and `/tmp/app-8002.log`.
