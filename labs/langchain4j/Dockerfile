FROM labbox/node:v1 AS node

FROM labbox/java:v1
USER root
RUN apt-get update && apt-get install -y --no-install-recommends jq && rm -rf /var/lib/apt/lists/*
# Node, only to run the filesystem MCP server of chapter 20 (npx is not needed: it is installed here, offline).
COPY --from=node /opt/node /opt/node
ENV PATH=/opt/node/bin:$PATH
RUN npm install -g --no-fund --no-audit @modelcontextprotocol/server-filesystem@2026.8.31 \
    && ln -s /opt/node/bin/mcp-server-filesystem /usr/local/bin/mcp-server-filesystem
# One shared local Maven repository, filled at build time, so builds work offline (checks have no network).
RUN mkdir -p /opt/m2 && chown 1000:1000 /opt/m2 \
    && sed -i 's|<!-- localRepository|<localRepository>/opt/m2</localRepository>\n  <!-- localRepository|' /opt/maven/conf/settings.xml
# The local embedding model's tokenizer caches a native library: keep it in the image, not in the home folder
# (a lab machine may mount its own home), so it works offline for learners and checks.
RUN mkdir -p /opt/djl && chown 1000:1000 /opt/djl
ENV DJL_CACHE_DIR=/opt/djl
COPY --chown=1000:1000 warm/ /tmp/warm/
USER 1000
RUN cd /tmp/warm && mvn -B -q dependency:go-offline && mvn -B -q package \
    && mvn -B -q -o test && mvn -B -q -o exec:java -Dexec.mainClass=com.setu.Warm \
    && for d in /tmp/warm/chapters/*/; do (cd "$d" && mvn -B -q dependency:go-offline) || exit 1; done \
    && rm -rf /tmp/warm
