# Changelog

## **2023.04.20-0.3.2**

- If you have a Serial, either try pymodbus serial or use mbusd

- update pymodbus to 3.2.2
  - Tcp seems to work (only been running for a short while)
  - Serial not tested

- umodbus
  - TCP is stable
  - Serial is currently not working

- paho-mqtt 1.6.1

## **2023.04.17-0.3.1**

- split out mqtt_entity

## **2023.03.19b-0.3.1**

- Fixed MQTT reconnect logic #94

## **2023.03.19-0.3.1**

- Initial release of the multi addon
- It only supports a single inverter today
- Select between single-phase & three-phase sensor definitions
- Supports custom sensors in /share/hass-addon-sunsynk/mysensors.py

