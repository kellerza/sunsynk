FROM ghcr.io/home-assistant/base-python:3.13-alpine3.22
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

LABEL maintainer="Johann Kellerman <kellerza@gmail.com>"

# Add uv to the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Install sunsynk from local source
COPY sunsynk sunsynk

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# modbus-rs only ships glibc/cp311 wheels, so on this musl + py3.13 base it is
# built from source. Alpine's rustc lags modbus-rs MSRV (e.g. napi-build needs 1.88),
# so install stable via rustup; build tools are removed after.
RUN set -x \
    && apk add --no-cache --virtual .build-deps curl build-base patchelf \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
        | sh -s -- -y --profile minimal \
    && source "$HOME/.cargo/env" \
    && uv venv \
    && uv pip install --index-strategy unsafe-best-match \
        ./sunsynk[modbusrs,solarman] \
    && apk del .build-deps \
    && rm -rf "$HOME/.cargo" "$HOME/.rustup"

COPY rootfs /
COPY VERSION VERSION
