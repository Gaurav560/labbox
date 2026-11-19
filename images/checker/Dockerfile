# labbox/checker: runs live checks against a learner's running system (never the learner's code).
FROM labbox/python:v1
USER root
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client redis-tools \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --break-system-packages requests==2.32.3 "psycopg[binary]==3.2.3" redis==5.2.1
USER 1000
# k6 (Grafana, AGPL-3.0, run as a separate tool) for load tests in system design labs.
COPY --from=grafana/k6:0.55.0 /usr/bin/k6 /usr/local/bin/k6
# Helper for live checks: run a k6 script, get p50/p95/p99, error rate, throughput and custom counters.
COPY labbox_k6.py /usr/lib/python3/dist-packages/labbox_k6.py
