FROM labbox/python:v1
USER root
# The base image is "minimized": no manual pages. Linux on call teaches `man`, so bring them back, and add the
# everyday tools the course uses (tree, file, lsof, ss from iproute2, jq, zip, htop, killall and pstree from psmisc, nc).
RUN rm -f /etc/dpkg/dpkg.cfg.d/excludes \
 && apt-get update \
 && apt-get install -y --no-install-recommends man-db manpages tree file lsof iproute2 jq zip unzip htop psmisc netcat-openbsd \
 && apt-get install -y --reinstall --no-install-recommends coreutils grep sed findutils procps tar gzip util-linux bash \
 && if [ -f /usr/bin/man.REAL ]; then rm -f /usr/bin/man && dpkg-divert --quiet --remove --rename /usr/bin/man; fi \
 && mandb -q \
 && rm -rf /var/lib/apt/lists/*
# Chapter setup scripts: they run as the learner (setup_user: learner) and build each chapter's folder.
COPY setup/ /lab/setup/
RUN chmod -R a+rX /lab
USER 1000
