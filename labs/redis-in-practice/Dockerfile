FROM labbox/python:v1
USER root
RUN apt-get update && apt-get install -y --no-install-recommends redis-tools \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --break-system-packages fastapi==0.115.6 "uvicorn[standard]==0.32.1" redis==5.2.1
# redis-cli talks to the lab's Redis (the service named redis) without typing -h every time.
RUN printf '#!/bin/sh\nexec /usr/bin/redis-cli -h "${REDIS_HOST:-redis}" "$@"\n' > /usr/local/bin/redis-cli \
    && chmod 755 /usr/local/bin/redis-cli
# The same for redis-benchmark (chapter 1 and 13 measure the lab's Redis).
RUN printf '#!/bin/sh\nexec /usr/bin/redis-benchmark -h "${REDIS_HOST:-redis}" "$@"\n' > /usr/local/bin/redis-benchmark \
    && chmod 755 /usr/local/bin/redis-benchmark
# Chapter setup scripts: run as root by LabBox, unreadable for the learner.
COPY setup/ /lab/setup/
RUN chmod -R go-rwx /lab
USER 1000
