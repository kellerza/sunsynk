# Sensors

You can add sensors under the `SENSORS` and `SENSORS_FIRST_INVERTER` keys in the configuration.

If you want to add the *Battery SOC* sensor, you can use any of the following formats. In the logs you will see the first format (no spaces and all lower case).

```yaml
SENSORS:
  - battery_soc
  - Battery SOC
  - battery_SOC
```

This page lists common sensors that can also be added through sensor groups. You can find all the supported sensor names in the sensor definition files, or even use the Modbus protocol document to create your own definitions.

## Sensor definitions

The sensor definitions include the modbus register number (or several registers), the name of the sensor, the unit and other optional parameters. For example:

```python
Sensor(183, "Battery voltage", VOLT, 0.01),
Sensor(184, "Battery SOC", "%"),
```

The last parameter in the battery voltage sensor definition is a factor, in this case a value of 1 in the register represents 0.01V. When the factor is negative for normal sensors it indicates that the number in the register is Signed (it can be negative & positive)

To enable both these sensors in your configuration, simply use the names:

```yaml
SENSORS:
  - battery_voltage
  - battery_soc
```

## Single Phase Inverter Sensor Definitions

You can find all the definitions here: <https://github.com/kellerza/sunsynk/blob/main/src/sunsynk/definitions.py>

These definitions are used when you configure a single-phase inverter in the addon:

```yaml
SENSOR_DEFINITIONS: single-phase
```

## Three Phase Inverter Sensor Definitions

You can find all the definitions here: <https://github.com/kellerza/sunsynk/blob/main/src/sunsynk/definitions3ph.py>

These definitions are used when you configure a three-phase inverter in the addon:

```yaml
SENSOR_DEFINITIONS: three-phase
```

## Groups of sensors

Sensor groups will allow you to add several sensors with a single entry.

### Energy management

These sensors are mostly related to energy or kWh and required for the Home Assistant [Energy Management](../guide/energy-management)

```yaml
SENSORS:
  - energy_management
```

::: details Sensors included

```yaml
total_battery_charge
total_battery_discharge
total_grid_export
total_grid_import
total_pv_energy
```

:::

### Power flow card: `power_flow_card`

These are all sensors used by the [Power Flow Card](../examples/lovelace#sunsynk-power-flow-card)

```yaml
SENSORS:
  - power_flow_card
```

::: details Sensors included

```yaml
aux_power
battery_current
battery_power
battery_soc
battery_voltage
day_battery_charge
day_battery_discharge
day_grid_export
day_grid_import
day_load_energy
day_pv_energy
essential_power
grid_connected
grid_ct_power
grid_frequency
grid_power
grid_voltage
inverter_current
inverter_power
load_frequency
non_essential_power
overall_state
priority_load
pv1_current
pv1_power
pv1_voltage
use_timer
```

:::

### Settings

Sensors used for changing the System Operating Mode - see [here](../examples/lovelace-settings)

These can be under `SENSORS` or `SENSORS_FIRST_INVERTER`

```yaml
SENSORS_FIRST_INVERTER:
  - settings
```

::: details Sensors included

```yaml
load_limit
prog1_capacity
prog1_charge
prog1_power
prog1_time
prog2_capacity
prog2_charge
prog2_power
prog2_time
prog3_capacity
prog3_charge
prog3_power
prog3_time
prog4_capacity
prog4_charge
prog4_power
prog4_time
prog5_capacity
prog5_charge
prog5_power
prog5_time
prog6_capacity
prog6_charge
prog6_power
prog6_time
```

:::

### Custom Sensors

If you have [custom sensors](./mysensors), you can add them all with the `mysensors` group.

```yaml
SENSORS:
  - mysensors
```
