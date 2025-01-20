# Sensors

::: tip
You can find all sensors names in the definitions here: <https://github.com/kellerza/sunsynk/blob/main/src/sunsynk/definitions>
:::

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

You can find the details of the definitions [here](https://github.com/kellerza/sunsynk/blob/main/src/sunsynk/definitions) and definitions are selected in the configuration with one of the following options:

```yaml
SENSOR_DEFINITIONS: single-phase / three-phase [low voltage] / three-phase-hv [high voltage]
```

## Groups of sensors

Sensor groups will allow you to add several sensors with a single entry.

### All sensors

The **all** group will include all the sensors available for your inverter.

```yaml
SENSORS:
  - all
```

Adding all sensors will cause Home Assistant to record a great amount of data, that you might not need. This could lead to a large database and slow down your system. It is especially bad if you are using an SD card for your Home Assistant installation.

Rather consider using the other groups or selecting the sensors you need.

::: warning
It is *not* recommended to add **all** sensors for your final system. This is mainly for testing purposes.
:::

### Energy management

These sensors are mostly related to energy or kWh and required for the Home Assistant [Energy Management](../guide/energy-management)

```yaml
SENSORS:
  - energy_management
```

::: details Sensors included

```yaml
SENSORS:
  - total_battery_charge
  - total_battery_discharge
  - total_grid_export
  - total_grid_import
  - total_pv_energy
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
SENSORS:
  - aux_power
  - battery_1_soc  # 3PH HV
  - battery_1_voltage  # 3PH HV
  - battery_current
  - battery_power
  - battery_soc  # 1PH & 3PH LV
  - battery_voltage  # 1PH & 3PH LV
  - day_battery_charge
  - day_battery_discharge
  - day_grid_export
  - day_grid_import
  - day_load_energy
  - day_pv_energy
  - essential_power
  - grid_connected
  - grid_ct_power
  - grid_current
  - grid_frequency
  - grid_l1_power  # 3PH LV & HV
  - grid_l2_power  # 3PH LV & HV
  - grid_l3_power  # 3PH LV & HV
  - grid_power
  - grid_voltage
  - inverter_current
  - inverter_power
  - inverter_voltage
  - load_frequency
  - load_power
  - load_l1_power
  - load_l2_power
  - load_l3_power
  - load_l1_voltage
  - load_l2_voltage
  - load_l3_voltage
  - non_essential_power
  - overall_state
  - priority_load
  - pv_power
  - pv1_current
  - pv1_power
  - pv1_voltage
  - pv2_current
  - pv2_power
  - pv2_voltage
  - pv3_current
  - pv3_power
  - pv3_voltage
  - pv4_current
  - pv4_power
  - pv4_voltage
  - use_timer
```

:::

### Settings

Sensors used for changing the System Operating Mode - see [here](../examples/lovelace-settings)

These can be under `SENSORS` or `SENSORS_FIRST_INVERTER`

```yaml
SENSORS_FIRST_INVERTER:
  - settings
```

::: details Sensors included in `settings`

```yaml
SENSORS_FIRST_INVERTER:
  - export_limit_power
  - grid_charge_enabled
  - load_limit
  - prog1_capacity
  - prog1_charge
  - prog1_power
  - prog1_time
  - prog2_capacity
  - prog2_charge
  - prog2_power
  - prog2_time
  - prog3_capacity
  - prog3_charge
  - prog3_power
  - prog3_time
  - prog4_capacity
  - prog4_charge
  - prog4_power
  - prog4_time
  - prog5_capacity
  - prog5_charge
  - prog5_power
  - prog5_time
  - prog6_capacity
  - prog6_charge
  - prog6_power
  - prog6_time
  - solar_export
  - use_timer
```

::: details Sensors included in the `advanced` group

```yaml
SENSORS:
  - battery_capacity_current
  - battery_charge_efficiency
  - battery_low_capacity
  - battery_max_charge_current
  - battery_max_discharge_current
  - battery_resistance
  - battery_restart_capacity
  - battery_shutdown_capacity
  - battery_type
  - battery_wake_up
  - configured_grid_frequency
  - configured_grid_phases
  - date_time
  - grid_charge_battery_current
  - grid_charge_start_battery_soc
  - grid_standard
  - track_grid_phase
  - ups_delay_time
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
SENSORS:
  - gen_signal_on
  - generator_charge_battery_current
  - generator_charge_enabled
  - generator_charge_start_battery_soc
  - generator_cooling_time
  - generator_max_operating_time
  - generator_off_soc
  - generator_on_soc
  - generator_port_usage
  - min_pv_power_for_gen_start
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
SENSORS:
  - battery_bms_alarm_flag
  - battery_bms_fault_flag
  - battery_bms_soh
  - battery_current
  - battery_power
  - battery_soc
  - battery_temperature
  - battery_voltage
  - dc_transformer_temperature
  - fan_warning
  - fault
  - grid_l1_voltage
  - grid_l2_voltage
  - grid_l3_voltage
  - grid_phase_warning
  - grid_relay_status
  - grid_voltage
  - inverter_l1_power
  - inverter_l2_power
  - inverter_l3_power
  - inverter_relay_status
  - lithium_battery_loss_warning
  - parallel_communication_quality_warning
  - radiator_temperature
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
SENSORS:
  - battery_absorption_voltage
  - battery_capacity_current
  - battery_charge_efficiency
  - battery_equalization_days
  - battery_equalization_hours
  - battery_equalization_voltage
  - battery_float_voltage
  - battery_low_capacity
  - battery_low_voltage
  - battery_max_charge_current
  - battery_max_discharge_current
  - battery_resistance
  - battery_restart_capacity
  - battery_restart_voltage
  - battery_shutdown_capacity
  - battery_shutdown_voltage
  - battery_type
  - battery_wake_up
```

:::

### My Sensors

You can create custom sensors by defining them in a file called `mysensors.py` in the `/share/hass-addon-sunsynk/` directory. This allows you to add sensors that are not included in the default definitions.

To create custom sensors:

1. Create the directory and file:

   ```bash
   /share/hass-addon-sunsynk/mysensors.py
   ```

2. Define your sensors in the file. Here's a basic example:

   ```python
   from sunsynk import AMPS, CELSIUS, KWH, VOLT, WATT
   from sunsynk.rwsensors import NumberRWSensor, SelectRWSensor
   from sunsynk.sensors import Sensor, SensorDefinitions, MathSensor

   # Initialize the sensor definitions
   SENSORS = SensorDefinitions()

   # Add your custom sensors
   SENSORS += (
       # Basic sensor example
       Sensor(178, "My Custom Power Sensor", WATT, -1),

       # Math sensor example (combining multiple registers)
       MathSensor((175, 172), "Custom Combined Power", WATT, factors=(1, 1)),

       # Read/Write sensor example
       NumberRWSensor(130, "Custom Control Setting", "%", min=0, max=100),
   )
   ```

3. Add your custom sensors to your configuration using either individual sensors or the `mysensors` group:

   ```yaml
   SENSORS:
     - mysensors  # Adds all custom sensors
     # Or add specific sensors:
     - my_custom_power_sensor
     - custom_combined_power
     - custom_control_setting
   ```

The sensor definition parameters are:

- First parameter: Register number(s)
- Second parameter: Sensor name
- Third parameter: Unit (WATT, VOLT, AMPS, etc.)
- Last parameter: Scale factor (optional)

You can create different types of sensors:

- `Sensor`: Basic read-only sensor
- `MathSensor`: Combines multiple registers with mathematical operations
- `NumberRWSensor`: Read/write sensor for configurable values
- `SelectRWSensor`: Read/write sensor with predefined options
- `SwitchRWSensor`: Read/write sensor for boolean values

Once defined, your custom sensors will be loaded automatically when the addon starts, and you'll see them listed in the startup logs:

```log
INFO    Importing /share/hass-addon-sunsynk/mysensors.py...
INFO      custom sensors: my_custom_power_sensor, custom_combined_power, custom_control_setting
```

All your [custom sensors](mysensors) can be added to the configuration using the `mysensors` group:

```yaml
SENSORS:
  - mysensors
```
