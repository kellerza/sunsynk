FROM ghcr.io/home-assistant/base-python:3.13-alpine3.22
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

LABEL maintainer="Johann Kellerman <kellerza@gmail.com>"

# Add uv to the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Install sunsynk from local source
COPY sunsynk sunsynk

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# modbus-rs only ships glibc/cp311 wheels, so on this musl + py3.13 base it is
# built from source. cargo/patchelf are only needed at build time and removed after.
RUN set -x \
    && apk add --no-cache --virtual .build-deps cargo patchelf \
    && uv venv \
    && uv pip install --index-strategy unsafe-best-match \
        ./sunsynk[modbusrs,solarman] \
    && apk del .build-deps

COPY rootfs /
COPY VERSION VERSION
