ARG BUILD_FROM
FROM ${BUILD_FROM}
COPY --from=ghcr.io/astral-sh/uv:0.6.2 /uv /uvx /bin/

LABEL maintainer="Johann Kellerman <kellerza@gmail.com>"

# Install sunsynk from local source
COPY sunsynk sunsynk

RUN set -x \
    && apk add --no-cache --virtual .build-deps \
        build-base \
    #&& curl -LsSf https://astral.sh/uv/0.6.2/install.sh | sh \
    #&& export PATH="$HOME/.local/bin:$PATH" \
    && uv venv \
    && uv pip install --index-strategy unsafe-best-match \
        aiohttp \
        ./sunsynk[umodbus,solarman] \
    && apk del .build-deps

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY rootfs /
