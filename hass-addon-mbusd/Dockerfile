ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk --no-cache add make cmake gcc g++ git pkgconf

RUN git clone https://github.com/3cky/mbusd.git /usr/src
RUN cd /usr/src && ls && cmake . && make && ls

WORKDIR /usr/src

#COPY /usr/src/mbusd /sbin/mbusd
COPY run.sh run.sh
ENTRYPOINT [ "./run.sh" ]

EXPOSE 502