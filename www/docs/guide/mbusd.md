# mbusd

mbusd is an open-source Modbus TCP to Modbus RTU (RS-232/485) gateway. It presents a network of RTU
servers as single TCP server.

That is a TCP server, which acts as an RTU client to get data from Modbus RTU servers. See
[Modbus](./overview.md#modbus) for client / server.

When you add the Sunsynk HASS repository, it includes a mbusd addon called "Modbus TCP to Modbus RTU
Gateway Add-on".

<https://github.com/kellerza/sunsynk/tree/main/hass-addon-mbusd>
