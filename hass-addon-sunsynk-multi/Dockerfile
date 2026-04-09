FROM ghcr.io/home-assistant/base-python:3.13-alpine3.22
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

LABEL maintainer="Johann Kellerman <kellerza@gmail.com>"

# Add uv to the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Install sunsynk from local source
COPY sunsynk sunsynk

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN set -x \
    && uv venv \
    && uv pip install --index-strategy unsafe-best-match \
        ./sunsynk[umodbus,solarman]

COPY rootfs /
COPY VERSION VERSION
