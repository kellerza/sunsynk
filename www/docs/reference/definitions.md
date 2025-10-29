# Sensors

## Sensor definitions

Your inverter exposes data/sensors in specific modbus registers. The inverter's modbus protocol
document will provide information of what the register represents and the format of the data in the
register.

The sensor definitions were created from these modbus protocol documents. Individual sensor
definitions   include the modbus register number (or several registers), the name of the sensor, the
unit and other optional parameters.

When you select your inverter type, the corresponding set of definitions will be used.

```yaml
SENSOR_DEFINITIONS: single-phase / three-phase [low voltage] / three-phase-hv [high voltage]
```

You can find the detail of the definitions
[on Github](https://github.com/kellerza/sunsynk/blob/main/src/sunsynk/definitions) and definitions
are selected in the configuration with one of the following options:

## Adding sensors

You can add sensors under the `SENSORS` and `SENSORS_FIRST_INVERTER` keys in the configuration.

For example, if you want to add the *Battery SOC* sensor, you can use any of the following formats.
In the logs you will see the first format (no spaces and all lower case).

```yaml
SENSORS:
  - battery_soc
  - Battery SOC
```

This page contains detail of available sensors. If you do not find the sensor you are looking for,
you can use the Modbus protocol document of your inverter to create your own custom sensor.

## Available sensors

The following table shows the sensor name and Modbus register(s) used to get/set the value.

<!--@include: ./groups/all.html-->

## Groups of sensors

Sensor groups will allow you to add several sensors with a single entry.

### All sensors

The **all** group will include all the sensors available for your inverter.

```yaml
SENSORS:
  - all
```

Adding all sensors will cause Home Assistant to record a great amount of data, that you might not
need. This could lead to a large database and slow down your system. It is especially bad if you are
using an SD card for your Home Assistant installation.

Rather consider using the other groups or selecting the sensors you need.

::: warning

It is *not* recommended to add **all** sensors for your final system. This is mainly for
testing purposes.

:::

### Energy management

These sensors are mostly related to energy or kWh and required for the Home Assistant
[Energy Management](../guide/energy-management)

```yaml
SENSORS:
  - energy_management
```

::: details Sensors included

```yaml
<!--@include: ./groups/energy_management.yml-->
```

:::

### Power Flow Card

These are all sensors used by the [Power Flow Card](../examples/lovelace#sunsynk-power-flow-card)

```yaml
SENSORS:
  - power_flow_card
```

::: details Sensors included

```yaml
<!--@include: ./groups/power_flow_card.yml-->
```

:::

### Settings

Sensors used for changing the System Operating Mode - see how they are used in
[Lovelace settings](../examples/lovelace-settings)

These can be under `SENSORS` or `SENSORS_FIRST_INVERTER`

```yaml
SENSORS_FIRST_INVERTER:
  - settings
```

::: details Sensors included in `settings`

```yaml
<!--@include: ./groups/settings.yml-->
```

::: details Sensors included in the `advanced` group

```yaml
<!--@include: ./groups/advanced.yml-->
```

:::

### Generator

Sensors used for generator control and monitoring.

```yaml
SENSORS:
  - generator
```

::: details Sensors included

```yaml
<!--@include: ./groups/generator.yml-->
```

:::

### Diagnostics

Sensors used for system diagnostics and monitoring.

```yaml
SENSORS:
  - diagnostics
```

::: details Sensors included

```yaml
<!--@include: ./groups/diagnostics.yml-->
```

:::

### Battery

Sensors used for battery configuration and management.

```yaml
SENSORS:
  - battery
```

::: details Sensors included

```yaml
<!--@include: ./groups/battery.yml-->
```

:::

### Parallel

Sensors used for parallel inverter configuration and management.

```yaml
SENSORS:
  - parallel
```

::: details Sensors included

```yaml
<!--@include: ./groups/parallel.yml-->
```

:::

### UPS / Backup Load

Sensors used for monitoring UPS (Uninterruptible Power Supply) or backup load power consumption.
These sensors provide power readings for each phase (L1, L2, L3) and total power consumption during
backup operation.

```yaml
SENSORS:
  - ups
```

::: details Sensors included

```yaml
<!--@include: ./groups/ups.yml-->
```

:::

### My Sensors

All your [Custom sensors](mysensors) can be added to the configuration using the **mysensors**
group:

```yaml
SENSORS:
  - mysensors
```

Refer to [Custom Sensors](mysensors) for more information.
