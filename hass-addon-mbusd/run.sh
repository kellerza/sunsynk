#!/usr/bin/env bashio

DEVICE=$(bashio::config 'DEVICE')
BAUDRATE=$(bashio::config 'BAUDRATE')
MODE=$(bashio::config 'MODE')
LOGLEVEL=$(bashio::config 'LOGLEVEL')
TIMEOUT=$(bashio::config 'TIMEOUT')

bashio::log.info "Starting mbusd -d -L - -v $LOGLEVEL -p $DEVICE -s $BAUDRATE -m $MODE -P 502"

exec /usr/src/mbusd -d -L - -v $LOGLEVEL -p $DEVICE -s $BAUDRATE -m $MODE -P 502 -T $TIMEOUT
