FROM labbox/python:v1
USER root
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*
# Chapter setup scripts: run as root by LabBox, unreadable for the learner (they would spoil the incident).
COPY setup/ /lab/setup/
RUN chmod -R go-rwx /lab
USER 1000
