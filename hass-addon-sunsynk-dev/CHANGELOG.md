# Changelog

## **2022.07.24-0.2.1** - 2022-07-24

- Python sunsynk module 0.2.1:

  - Introduced NumberRWSensor - [#37](https://github.com/kellerza/sunsynk/issues/37)

- Sunsynk Dev Add-On
  - Use Home Assistant MQTT Number integration when encountering NumberRWSensor
  - Prog1 to 6 battery capacity and power sensors are now editable in the Home
    Assistant UI
  - Added Rated Power to device model

## **2022.07.11-0.2.0** - 2022-07-11

- Python sunsynk module 0.2.0:

  - Deprecate Time x Power sensors in favour of Energy - [#27](https://github.com/kellerza/sunsynk/issues/27)

- Sunsynk Add-On
  - Fix RR filter

- Sunsynk Dev Add-On
  - Fix RR filter
  - Add **DEVICE** option as an alternative to **PORT**. **DEVICE** should list all available tty device in HASS IO and will be used if the **PORT** is empty

## **2022.05.29b-0.1.5** - 2022-05-29

- Python sunsynk module 0.1.5:

  - Added read_sensors_batch_size field to allow for customizing how many holding registers are read at a time from the inverter. Certain implementations, such as using a USR-W630, require less registers to be read at a time, otherwise the modbus response can be truncated, leading to errors. The default is 60, which matches the previous behaviour.

- Sunsynk Dev Add-On

  - Added READ_SENSORS_BATCH_SIZE option to expose the read_sensors_batch_size field from the sunsynk module.

## **2022.2.18-0.1.3** - 2022-02-18

- Python sunsynk module 0.1.3:

  - More consistent sensor names: Power (W) based sensors now all end with \_power: aux_power, inverter_output_power, grid_power, grid_ct_power

  - Added "essential_power" & "non_essential_power" sensor, which is a combination of registers

  - New: battery_charging_voltage, grid_charge_enabled

- Sunsynk Dev Add-On

  Better error handling

## **2022.2.17b-0.1.2** - 2022-02-17

- Sunsynk Dev Add-On

- Fix step filter bug
- Use async_modbus / umodbus

## **2022.2.10-0.1.2** - 2022-02-08

Python sunsynk module 0.1.2:

- Add sensors

Sunsynk Add-On:

- Fail after multiple read errors

## **2022.2.8-0.1.1** - 2022-02-08

Python sunsynk module 0.1.1:

- Fix debug print

Sunsynk Add-On:

- Improve exception handling on read

## **2022.2.6-0.1.0** - 2022-02-06

- Timeout on first read

## **2022.2.5-0.1.0** - 2022-02-05

Major update

Python sunsynk module 0.1.0:

- Modified definitions
- Writing registers

Sunsynk Add-On:

- Modify settings with presets (BETA)
- New MQTT select entity
- No more restart on Timeouts
- Filter updates (support strings)

## **2022.1.26-0.0.8** - 2022-01-26

- Added grid_voltage
- HASS addon: Sensor availability using MQTT LWT
- HASS addon: Less debug info
- HASS addon: sensor prefix
- HASS addon: New filter option: now

## **2021.10.1-0.0.7** - 2021-10-19

- Quit on Modbus disconnect,- watchdog can restart

## **2021.10.0-0.0.7** - 2021-09-30

- Add a configurable timeout

## **2021.9.20-0.0.6** - 2021-09-30

- Allow TCP connections (PORT_ADDRESS)
- Sunsynk: Async connect
- Sunsynk: Faults & connection exceptions

## **2021.9.19-0.0.5** - 2021-09-22

- Updated definitions & decoding
- Unit tests

## **2021.9.16-0.0.4** - 2021-09-22

- Fix battery_soc

## **2021.9.15-0.0.4** - 2021-09-22

- Enforce Sunsynk Serial number as SUNSYNK_ID
- Library cleanup

## **2021.9.8** - 2021-09-21

- MQTT: Clean retain config for unused sensors
- Added filters

## **2021.9.2** - 2021-09-15

### Changed

- Initial version
