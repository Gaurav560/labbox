# labbox/checker: runs live checks against a learner's running system (never the learner's code).
FROM labbox/python:v1
USER root
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client redis-tools \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --break-system-packages requests==2.32.3 "psycopg[binary]==3.2.3" redis==5.2.1
USER 1000
