ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG UV_VERSION=0.9.5

LABEL maintainer="Johann Kellerman <kellerza@gmail.com>"

# Add uv to the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Install sunsynk from local source
COPY sunsynk sunsynk

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN set -x \
    && curl -LsSf https://astral.sh/uv/${UV_VERSION}/install.sh | sh \
    && uv venv \
    && uv pip install --index-strategy unsafe-best-match \
        ./sunsynk[umodbus,solarman]

COPY rootfs /
