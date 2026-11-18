# labbox/node: Node.js 22 LTS with npm (official binaries from nodejs.org).
FROM labbox/base:v1
USER root
ARG NODE_VERSION=22.23.5
RUN apt-get update && apt-get install -y --no-install-recommends xz-utils && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" \
      | tar -xJ -C /opt && ln -s /opt/node-v${NODE_VERSION}-linux-x64 /opt/node
ENV PATH=/opt/node/bin:$PATH NPM_CONFIG_UPDATE_NOTIFIER=false
USER 1000
