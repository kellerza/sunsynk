# Changelog

## **2023.05.18-0.3.5**

- sunsynk 0.3.5
  - Reworked 1ph essentials sensor - refer to definitions.py
       Essential power
       - https://powerforum.co.za/topic/8646-my-sunsynk-8kw-data-collection-setup/?do=findComment&comment=147591
       Essential old power
       - dev & normal version, see https://github.com/kellerza/sunsynk/issues/134
       Essential abs power
       - early-2023 see https://github.com/kellerza/sunsynk/issues/75

  - Additional sensors to support all the options in @slipx's power flow card
    - Inverter Current
    - Generator Input (235) - this might explain the difference on the essentials sensor value...
    - Use Timer - see https://github.com/kellerza/sunsynk/discussions/137

## **2023.05.05-0.3.4**

- sunsynk 0.3.4
  - Improve test coverage

- Multi-Addon
  - multiple inverters beta release (`SENSORS_FIRST_INVERTER` not yet supported)
  - Improve test coverage

## **2023.04.22-0.3.3**

- sunsynk 0.3.3
  - Update pysunsynk driver
  - Added date sensor (MQTT text entity)
  - Improve test coverage
  - Changed switch entity

- Multi-Addon

## **2023.04.20-0.3.2**

- If you have a Serial, either try pymodbus serial or use mbusd

- update pymodbus to 3.2.2
  - Tcp seems to work (only been running for a short while)
  - Serial not tested

- umodbus
  - TCP is stable
  - Serial is currently not working

- paho-mqtt 1.6.1

- **2023.04.20b-0.3.2**  - bugfix log


## **2023.04.17-0.3.1**

- split out mqtt_entity

## **2023.03.19b-0.3.1**

- Fixed MQTT reconnect logic #94

## **2023.03.19-0.3.1**

- Initial release of the multi addon
- It only supports a single inverter today
- Select between single-phase & three-phase sensor definitions
- Supports custom sensors in /share/hass-addon-sunsynk/mysensors.py

