ARG BASE=ghcr.io/home-assistant/base:3.22

# mbusd Dockerfile as reference https://github.com/3cky/mbusd/blob/master/Dockerfile
# - FROM home-assistant/base iso alpine:latest
# - Clone a specific git tag from https://github.com/3cky/mbusd/releases
FROM ${BASE} AS build
RUN apk add --no-cache alpine-sdk cmake linux-headers git
WORKDIR /usr/src
RUN git clone --depth 1 --branch v0.5.3 https://github.com/3cky/mbusd.git
RUN cd mbusd \
    && cmake -DCMAKE_INSTALL_PREFIX=/usr . \
    && make && make install

FROM ${BASE} AS runtime
ENV QEMU_EXECVE=1
COPY --from=build /usr/bin/mbusd /usr/bin/mbusd
WORKDIR /usr/src
COPY run.sh run.sh
ENTRYPOINT [ "./run.sh" ]

EXPOSE 502
