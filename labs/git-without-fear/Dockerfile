FROM labbox/base:v1
USER root
# Chapter setup scripts: they run as the learner (setup_user: learner) and only build the practice repos.
COPY setup/ /lab/setup/
RUN chmod -R a+rX /lab
USER 1000
