# labbox/base: what every lab machine shares. Learner is uid 1000 with a home folder.
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8
RUN apt-get update && apt-get install -y --no-install-recommends \
      bash ca-certificates curl git less nano procps vim-tiny \
    && rm -rf /var/lib/apt/lists/*
# Ubuntu ships a uid 1000 user (ubuntu): rename it to learner and drop its extra groups.
RUN usermod -l learner -d /home/learner -m -s /bin/bash -G "" ubuntu && groupmod -n learner ubuntu
ENV PS1="\[\e[32m\]learner\[\e[0m\]:\[\e[34m\]\w\[\e[0m\]$ "
USER 1000
WORKDIR /workspace
CMD ["sleep", "infinity"]
