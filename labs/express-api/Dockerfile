FROM labbox/node:v1
USER root
# Express lives in the image (not in the workspace), so it works offline and inside checks.
RUN mkdir -p /opt/labdeps && cd /opt/labdeps && npm init -y >/dev/null && npm install --omit=dev express@5.3.0 \
    && npm cache clean --force
ENV NODE_PATH=/opt/labdeps/node_modules
USER 1000
