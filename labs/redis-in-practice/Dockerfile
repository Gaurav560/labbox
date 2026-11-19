FROM labbox/python:v1
USER root
RUN apt-get update && apt-get install -y --no-install-recommends redis-tools \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --break-system-packages fastapi==0.115.6 "uvicorn[standard]==0.32.1" redis==5.2.1
# redis-cli talks to the lab's Redis (the service named redis) without typing -h every time.
RUN printf '#!/bin/sh\nexec /usr/bin/redis-cli -h "${REDIS_HOST:-redis}" "$@"\n' > /usr/local/bin/redis-cli \
    && chmod 755 /usr/local/bin/redis-cli
USER 1000
