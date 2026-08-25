# mbusd

mbusd is an open-source Modbus TCP to Modbus RTU (RS-232/485) gateway. It presents a network of RTU
servers as single TCP server.

That is a TCP server, which acts as an RTU client to get data from Modbus RTU servers. See
[Modbus](./overview.md#modbus) for client / server.

When you add the Sunsynk HASS repository, it includes a mbusd addon called "Modbus TCP to Modbus RTU
Gateway Add-on".

<https://github.com/kellerza/sunsynk/tree/main/hass-addon-mbusd>

Point the Sunsynk add-on at `tcp://homeassistant.local:502` (or the host that runs mbusd). mbusd has
its own wait/retry on the RS485 leg — in add-on language that is **3** `READ_ATTEMPTS`, **500 ms**
`TIMEOUT` (`-W`), and **100 ms** `READ_MESSAGE_SPACING` (`-R`). Keep that RTU wait shorter than the
Sunsynk add-on's `TIMEOUT`. Comparison table:
[Wait times by component](../reference/multi-options#wait-times-by-component).
