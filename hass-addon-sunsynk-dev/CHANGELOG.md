# Changelog

## **2022.2.18-0.1.3** - 2022-02-18

- Python sunsynk module 0.1.3:

  - More consistent sensor names: Power (W) based sensors now all end with _power: aux_power, inverter_output_power, grid_power, grid_ct_power

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
