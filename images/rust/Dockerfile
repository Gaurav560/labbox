# labbox/rust: the Rust toolchain (rustup, a pinned stable release, rustfmt and clippy), and a C linker.
FROM labbox/base:v1
USER root
ARG RUST_VERSION=1.100.0
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev python3 \
    && rm -rf /var/lib/apt/lists/*
ENV RUSTUP_HOME=/opt/rustup CARGO_HOME=/opt/cargo PATH=/opt/cargo/bin:$PATH
RUN curl -fsSL https://sh.rustup.rs -o /tmp/rustup.sh \
    && sh /tmp/rustup.sh -y --no-modify-path --profile minimal --default-toolchain "$RUST_VERSION" \
         --component rustfmt,clippy \
    && rm /tmp/rustup.sh && mkdir -p /opt/rust-target \
    && chown -R 1000:1000 /opt/cargo /opt/rust-target
# Lab machines and checks have no internet: crates come from the cache the lab image fills.
# One shared build folder keeps compiled crates between chapters and checks.
ENV CARGO_NET_OFFLINE=true CARGO_TARGET_DIR=/opt/rust-target CARGO_TERM_COLOR=never CARGO_BUILD_JOBS=4
USER 1000
