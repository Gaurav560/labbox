FROM labbox/java:v1
USER root
RUN apt-get update && apt-get install -y --no-install-recommends jq && rm -rf /var/lib/apt/lists/*
# One shared local Maven repository, filled at build time, so builds work offline (checks have no network).
RUN mkdir -p /opt/m2 && chown 1000:1000 /opt/m2 \
    && sed -i 's|<!-- localRepository|<localRepository>/opt/m2</localRepository>\n  <!-- localRepository|' /opt/maven/conf/settings.xml
COPY --chown=1000:1000 warm/ /tmp/warm/
USER 1000
RUN cd /tmp/warm && mvn -B -q dependency:go-offline && mvn -B -q package && mvn -B -q -o test && rm -rf /tmp/warm
