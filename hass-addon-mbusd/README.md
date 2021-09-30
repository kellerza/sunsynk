# Modbus TCP to Modbus RTU Gateway Add-on

This Add-on uses the [mbusd](https://github.com/3cky/mbusd) gateway. It provides a TCP-Slave (or server) which acts as a RTU-master to get data from Modbus RTU-slave devices.

I use this mainly for testing, but mbusd can also be deployed on a low-spec device (i.e. Raspberry Pi 1b) to convert an RS-485 connection to TCP.

## Configuration

Refer to the [mbusd](https://github.com/3cky/mbusd#usage) command line options for more detail.
