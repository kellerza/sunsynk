ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base

# mbusd Dockerfile as reference https://github.com/3cky/mbusd/blob/master/Dockerfile
# - FROM home-assistant/base iso alpine:latest
# - Clone a specific git tag from https://github.com/3cky/mbusd/releases
FROM ${BUILD_FROM} AS build
RUN apk add --no-cache alpine-sdk cmake linux-headers git
WORKDIR /usr/src
RUN git clone --depth 1 --branch v0.5.2 https://github.com/3cky/mbusd.git
RUN cd mbusd \
    && cmake -DCMAKE_INSTALL_PREFIX=/usr . \
    && make && make install

FROM ${BUILD_FROM} AS runtime
COPY --from=build /usr/bin/mbusd /usr/bin/mbusd
WORKDIR /usr/src
COPY run.sh run.sh
ENTRYPOINT [ "./run.sh" ]

EXPOSE 502
