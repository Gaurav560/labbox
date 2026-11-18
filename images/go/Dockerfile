# labbox/go: the Go toolchain (official binaries from go.dev).
FROM labbox/base:v1
USER root
ARG GO_VERSION=1.27.4
RUN curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" | tar -xz -C /opt \
    && mkdir -p /opt/gocache && chown 1000:1000 /opt/gocache
# A shared, pre-warmed build cache: without it every check rebuilds the standard library (about 30 s).
ENV PATH=/opt/go/bin:/home/learner/go/bin:$PATH GOPATH=/home/learner/go GOCACHE=/opt/gocache \
    GOTOOLCHAIN=local GOTELEMETRY=off
USER 1000
RUN mkdir -p /tmp/warm && cd /tmp/warm \
    && printf 'module warm\n\ngo 1.27\n' > go.mod \
    && printf 'package warm\n\nimport (\n\t"encoding/json"\n\t"fmt"\n\t"sort"\n\t"strings"\n)\n\nvar _ = json.Marshal\nvar _ = fmt.Sprint\nvar _ = sort.Ints\nvar _ = strings.Split\n' > warm.go \
    && printf 'package warm\n\nimport "testing"\n\nfunc TestWarm(t *testing.T) {}\n' > warm_test.go \
    && go vet . && go test -count=1 . && go build ./... && cd / && rm -rf /tmp/warm
