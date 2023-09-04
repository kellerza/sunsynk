ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN set -x \
    && apk add --no-cache --virtual .build-deps \
        build-base \
    && pip3 install aiohttp==3.8.5 --no-cache-dir --disable-pip-version-check \
    && apk del .build-deps

RUN pip3 install sunsynk[pymodbus,umodbus,solarman]==0.5.8 --no-cache-dir --disable-pip-version-check

# Install sunsynk from local source
#! COPY sunsynk sunsynk
#! RUN pip3 install -e sunsynk[pymodbus,umodbus,solarman] --no-cache-dir --disable-pip-version-check

COPY rootfs /

#! RUN chmod a+x /etc/services.d/sunsynk/run
#! RUN chmod a+x /etc/services.d/sunsynk/finish
