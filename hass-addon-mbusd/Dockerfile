ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN \
    apk --no-cache add  --virtual .build-deps \
        make cmake gcc g++ git pkgconf \
    && git clone --depth 1 --branch v0.5.2 \
        https://github.com/3cky/mbusd.git /usr/src \
    && cd /usr/src \
    && ls \
    && cmake . \
    && make \
    && apk del .build-deps

WORKDIR /usr/src

COPY run.sh run.sh
ENTRYPOINT [ "./run.sh" ]

EXPOSE 502
