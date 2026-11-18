FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends bash git nano less procps \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pytest==8.3.3
RUN useradd -m -u 1000 -s /bin/bash learner
USER learner
WORKDIR /workspace
ENV PS1="\[\e[32m\]learner\[\e[0m\]:\[\e[34m\]\w\[\e[0m\]$ "
CMD ["sleep", "infinity"]
