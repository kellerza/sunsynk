# Changelog

## **2023.01.12-0.2.7** - 2022-11-29

- Python sunsynk module 0.2.7:
  - Add bitmask sensors to support Modes (GM/BM/CM)

- Sunsynk Dev Add-On:
  - Update to use the latest sensors

## **2023.01.02-0.2.6** - 2022-11-29

- Python sunsynk module 0.2.6:
  - Add Load Limit RW Sensor (Zero Export & Limit to Load)

- Sunsynk Dev Add-On:
  - Always update config entity state after discovery
  - Round floats to 3 decomal place instead of 2

## **2022.12.29b-0.2.5** - 2022-11-29

- Sunsynk Dev Add-On:
  - Deprecate PROFILES (System Mode & System Mode Voltages)
  - Retain MQTT messages for configuration sensors (partially solves #78)

## **2022.11.29-0.2.5** - 2022-11-29

- Sunsynk Dev Add-On: Update apparent_power
- Sunsynk Addon: Sync to Dev. The normal addon will get all the new capabilities of the DEV addon, capability to update settings etc.

  **BREAKING CHANGE**:

  - Please ensure you make a copy of your settings (Ideally in Yaml)
  - Update the addon and click on the three dots to "Reset to defaults"
  - Ensure that you fill in the correct ID, MQTT details and SENSORS from your old config.


## **2022.09.16-0.2.5** - 2022-09-16

- Sunsynk Dev Add-On

  - Allow for customizing the `mode` of NumberEntity sensors allowing for forcing either `box` or `slider` mode instead of the default `auto` - requires Home Assistant 2022.9.0 for the effect to be seen - [#58](https://github.com/kellerza/sunsynk/pull/58)

## **2022.09.15-0.2.5** - 2022-09-15

- Sunsynk Dev Add-On

  - Suggested filter for all RWSensors is now round_robin [#61](https://github.com/kellerza/sunsynk/issues/61)
  - Filters now also get updated when force publishing sensor values

## **2022.08.30-0.2.5** - 2022-08-30

- Python sunsynk module 0.2.5:

  - Introduced new _Battery Shutdown voltage_, _Battery Restart voltage_ and _Battery Low Voltage_ sensors
  - Introduced new _Battery Float voltage_ sensor upon which the _Prog1-6 Voltage_ sensors depend
  - Made _Prog1-6 Charge_ and _Prog1-6 Voltage_ sensors writable
  - Made _Equalization voltage_ and _Absorption voltage_ writable and renamed them to have a _Battery_ prefix
  - Made _Battery Shutdown Capacity_, _Battery Restart Capacity_ and _Battery Low Capacity_ writable
  - Corrected _Prog1-6 Voltage_ factor to be 0.01

- Sunsynk Dev Add-On

  - For NumberEntity, use a step value to 0.1 if the factor of the sensor is less than 1

## **2022.08.27-0.2.4** - 2022-08-27

- Python sunsynk module 0.2.4:

  - Added on_change callback on Sensor class allowing for reacting to value changes
  - Changed battery shutdown, restart and low capacity sensors to be instances of RWSensor in prepraration for them to become writable and to distinguish them from the battery SOC sensors

- Sunsynk Dev Add-On

  - Update HASS discovery info for a sensor's dependants when its value changes
  - Automatically add sensor dependencies, if not specified in OPTS, as hidden sensors
  - HASS device_class is no longer set for RWSensor entities
  - Added icons for RWSensor entities

## **2022.08.21-0.2.3** - 2022-08-21

- Python sunsynk module 0.2.3:

  - Made TimeRWSensor writable - [#37](https://github.com/kellerza/sunsynk/issues/37)
  - Updated Prog1..6 Time sensors to have min/max values

- Sunsynk Dev Add-On
  - Use Home Assistant MQTT Select integration for TimeRWSensors

## **2022.08.01-0.2.2** - 2022-08-01

- Python sunsynk module 0.2.2:

  - Introduced SelectRWSensor - [#37](https://github.com/kellerza/sunsynk/issues/37)
  - Added "priority_mode" writable sensor allowing switching between battery and load priorities
  - NumberRWSensor now supports factor and validates min/max

- Sunsynk Dev Add-On
  - Use Home Assistant MQTT Select integration when encountering SelectRWSensor
  - The "priority_mode" sensor is now available as a Select entity

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
