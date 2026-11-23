# Rust from zero: the toolchain, every crate the course uses (downloaded, so the lab needs no internet), and
# those crates compiled in advance into the shared build folder, so a check compiles only the learner's code.
FROM labbox/rust:v1
COPY --chown=1000:1000 warm /tmp/warm
RUN cd /tmp/warm && CARGO_NET_OFFLINE=false cargo fetch -q \
    && for p in warm-errors warm-cli warm-async warm-web; do cargo test -q --no-run -p "$p" && cargo build -q -p "$p"; done \
    && rm -rf /tmp/warm
