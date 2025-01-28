ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install sunsynk from local source
COPY sunsynk sunsynk

RUN set -x \
    && apk add --no-cache --virtual .build-deps \
        build-base \
    && pip3 install --no-cache-dir --disable-pip-version-check \
        aiohttp \
        ./sunsynk[pymodbus,umodbus,solarman] \
    && apk del .build-deps

COPY rootfs /
