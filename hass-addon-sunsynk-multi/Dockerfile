ARG BUILD_FROM
FROM ${BUILD_FROM}
# COPY --from=ghcr.io/astral-sh/uv:0.6.2 /uv /uvx /bin/

LABEL maintainer="Johann Kellerman <kellerza@gmail.com>"

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Install sunsynk from local source
COPY sunsynk sunsynk

RUN set -x \
    && apk add --no-cache --virtual .build-deps \
        build-base \
    # && curl -LsSf https://astral.sh/uv/0.6.2/install.sh | sh \
    # && export PATH="$HOME/.local/bin:$PATH" \
    && uv venv \
    && uv pip install --index-strategy unsafe-best-match \
        aiohttp \
        ./sunsynk[umodbus,solarman] \
    && apk del .build-deps

# ENV VIRTUAL_ENV=/app/.venv
# ENV PATH="/app/.venv/bin:$PATH"

COPY rootfs /
