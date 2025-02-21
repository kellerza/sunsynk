ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install sunsynk from local source
COPY sunsynk sunsynk

RUN set -x \
    && apk add --no-cache --virtual .build-deps \
        build-base \
    && curl -LsSf https://astral.sh/uv/0.6.2/install.sh | sh \
    && export PATH="$HOME/.local/bin:$PATH" \
    && uv venv \
    && uv pip install --index-strategy unsafe-best-match \
        aiohttp \
        ./sunsynk[umodbus,solarman] \
    && apk del .build-deps

COPY rootfs /
