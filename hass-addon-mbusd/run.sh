#!/usr/bin/env bashio

if [ -z "${DEVICE+x}" ]; then
    DEVICE=$(bashio::config 'DEVICE')
fi

if [ -z "${BAUDRATE+x}" ]; then
  BAUDRATE=$(bashio::config 'BAUDRATE')
fi

if [ -z "${MODE+x}" ]; then
  MODE=$(bashio::config 'MODE')
fi

if [ -z "${LOGLEVEL+x}" ]; then
  LOGLEVEL=$(bashio::config 'LOGLEVEL')
fi

if [ -z "${TIMEOUT+x}" ]; then
  TIMEOUT=$(bashio::config 'TIMEOUT')
fi

bashio::log.info "Starting mbusd -d -L - -v $LOGLEVEL -p $DEVICE -s $BAUDRATE -m $MODE -P 502"

exec /usr/src/mbusd -d -L - -v $LOGLEVEL -p $DEVICE -s $BAUDRATE -m $MODE -P 502 -T $TIMEOUT
