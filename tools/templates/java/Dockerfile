FROM eclipse-temurin:21-jdk
RUN apt-get update && apt-get install -y --no-install-recommends bash nano less procps \
    && rm -rf /var/lib/apt/lists/*
# The temurin image already ships a uid 1000 user (ubuntu). Rename it to learner so the
# prompt and home folder match the other labs; create it if it does not exist.
RUN if id -u 1000 >/dev/null 2>&1; then \
      old="$(id -nu 1000)"; oldgroup="$(id -gn 1000)"; \
      usermod -l learner -d /home/learner -m -s /bin/bash -G "" "$old" && groupmod -n learner "$oldgroup"; \
    else \
      useradd -m -u 1000 -s /bin/bash learner; \
    fi
ENV PS1="\[\e[32m\]learner\[\e[0m\]:\[\e[34m\]\w\[\e[0m\]$ "
USER 1000
WORKDIR /workspace
CMD ["sleep", "infinity"]
