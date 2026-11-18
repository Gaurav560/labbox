# labbox/java: Eclipse Temurin 21 and Maven.
FROM eclipse-temurin:21-jdk AS jdk
FROM labbox/base:v1
USER root
COPY --from=jdk /opt/java/openjdk /opt/java/openjdk
ARG MAVEN_VERSION=3.9.9
RUN curl -fsSL "https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz" \
      | tar -xz -C /opt && ln -s /opt/apache-maven-${MAVEN_VERSION} /opt/maven
ENV JAVA_HOME=/opt/java/openjdk PATH=/opt/java/openjdk/bin:/opt/maven/bin:$PATH
USER 1000
