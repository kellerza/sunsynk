# Lovelace examples

This page contains a couple of frontend examples to represent the power flow of your system. While the Home Assistant Energy dashboard gives you a good indication of your energy usage, the power flow shows you what is happening at the current moment.

## Sunsynk Power Flow Card

The Sunsynk Power Flow card can be installed by adding a custom Lovelace repository to HACS: <https://github.com/slipx06/sunsynk-power-flow-card> or clicking this button:

[![Open your Home Assistant instance and open slipx's repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=sunsynk-power-flow-card&category=plugin&owner=slipx06)

![Power Flow Card](../images/power-flow.png =500x600)

```yaml
SENSORS:
  - power_flow_card
```

::: details Lovelace yaml

```yaml
type: custom:sunsynk-power-flow-card
cardstyle: compact
large_font: true
show_solar: true
inverter:
  modern: true
  autarky: power
battery:
  energy: 10640
  shutdown_soc: 15
  show_daily: true
  animation_speed: 6
  max_power: 4100
  show_absolute: true
  show_remaining_energy: true
  animate: true
solar:
  show_daily: true
  mppts: 2
  animation_speed: 9
  max_power: 5500
  display_mode: 2
  pv1_max_power: 2250
  pv2_max_power: 2250
  efficiency: 3
load:
  show_daily: true
  show_aux: false
  load1_name: Geyser
  load1_icon: boiler
  animation_speed: 8
  max_power: 8000
  dynamic_colour: true
  dynamic_icon: true
  path_threshold: 90
grid:
  show_daily_buy: true
  no_grid_colour:
    - 125
    - 125
    - 125
  show_nonessential: false
  animation_speed: 8
  max_power: 8000
  grid_off_colour:
    - 220
    - 4
    - 4
  grid_name: " "
entities:
  use_timer_248: switch.ss_use_timer
  priority_load_243: switch.ss_priority_load
  inverter_voltage_154: sensor.ss_inverter_voltage
  load_frequency_192: sensor.ss_load_frequency
  inverter_current_164: sensor.ss_inverter_current
  inverter_power_175: sensor.ss_inverter_power
  grid_connected_status_194: binary_sensor.ss_grid_connected
  inverter_status_59: sensor.ss_overall_state
  day_battery_charge_70: sensor.ss_day_battery_charge
  day_battery_discharge_71: sensor.ss_day_battery_discharge
  battery_voltage_183: sensor.ss_battery_voltage
  battery_soc_184: sensor.ss_battery_soc
  battery_power_190: sensor.ss_battery_power
  battery_current_191: sensor.ss_battery_current
  grid_power_169: sensor.ss_grid_power
  day_grid_import_76: sensor.ss_day_grid_import
  grid_ct_power_172: sensor.ss_grid_power
  day_load_energy_84: sensor.ss_day_load_energy
  essential_power: sensor.ss_essential_1_power
  nonessential_power: none
  aux_power_166: none
  day_pv_energy_108: sensor.ss_day_pv_energy
  pv1_power_186: sensor.ss_pv1_power
  pv2_power_187: sensor.ss_pv2_power
  pv1_voltage_109: sensor.ss_pv1_voltage
  pv1_current_110: sensor.ss_pv1_current
  pv2_voltage_111: sensor.ss_pv2_voltage
  pv2_current_112: sensor.ss_pv2_current
  prog1_time: select.ss_prog1_time
  prog1_capacity: number.ss_prog1_capacity
  prog1_charge: select.ss_prog1_charge
  prog2_time: select.ss_prog2_time
  prog2_capacity: number.ss_prog2_capacity
  prog2_charge: select.ss_prog2_charge
  prog3_time: select.ss_prog3_time
  prog3_capacity: number.ss_prog3_capacity
  prog3_charge: select.ss_prog3_charge
  prog4_time: select.ss_prog4_time
  prog4_capacity: number.ss_prog4_capacity
  prog4_charge: select.ss_prog4_charge
  prog5_time: select.ss_prog5_time
  prog5_capacity: number.ss_prog5_capacity
  prog5_charge: select.ss_prog5_charge
  prog6_time: select.ss_prog6_time
  prog6_capacity: number.ss_prog6_capacity
  prog6_charge: select.ss_prog6_charge
  radiator_temp_91: sensor.ss_radiator_temperature
  dc_transformer_temp_90: sensor.ss_dc_transformer_temperature
  total_pv_generation: sensor.ss_total_pv_energy
  remaining_solar: sensor.energy_production_today_remaining
dynamic_line_width: true
min_line_width: 2
```

:::

## Power Distribution card

The Lovelace configuration for the Power Distribution Card is shown below. You can install the Power Distribution Card through HACS

![Power distribution](../images/power_dist.webp)

::: details Required sensors

```yaml
SENSORS:
  - pv1_power
  - essential_power
  - battery_power
  - battery_soc
  - non_essential_power
  - grid_ct_power
```

:::

::: details Lovelace yaml

```yaml
type: custom:power-distribution-card
title: ''
entities:
  - decimals: ''
    display_abs: true
    name: solar
    unit_of_display: W
    icon: mdi:solar-power
    producer: true
    entity: sensor.ss_pv1_power
    threshold: ''
    preset: solar
    icon_color:
      equal: ''
      smaller: ''
  - decimals: ''
    display_abs: true
    name: home
    unit_of_display: W
    consumer: true
    icon: mdi:home-assistant
    invert_value: true
    entity: sensor.ss_essential_power
    color_threshold: '0'
    threshold: ''
    preset: home
    icon_color:
      bigger: ''
      equal: ''
      smaller: ''
    arrow_color:
      bigger: ''
      equal: ''
      smaller: ''
  - decimals: ''
    display_abs: true
    name: battery
    unit_of_display: W
    consumer: true
    icon: mdi:battery-outline
    producer: true
    entity: sensor.ss_battery_power
    threshold: ''
    preset: battery
    icon_color:
      bigger: ''
      equal: ''
      smaller: ''
    secondary_info_attribute: ''
    battery_percentage_entity: sensor.ss_battery_soc
  - decimals: ''
    display_abs: true
    name: pool
    unit_of_display: W
    invert_value: true
    consumer: true
    icon: mdi:pool
    entity: sensor.ss_non_essential_power
    color_threshold: '0'
    preset: pool
    threshold: ''
    icon_color:
      bigger: ''
      equal: ''
      smaller: ''
    arrow_color:
      bigger: ''
      equal: ''
      smaller: ''
  - decimals: ''
    display_abs: true
    name: grid
    unit_of_display: W
    icon: mdi:transmission-tower
    entity: sensor.ss_grid_ct_power
    preset: grid
    threshold: ''
    icon_color:
      equal: ''
      smaller: ''
    double_tap_action:
      action: navigate
      navigation_path: /lovelace/power
    tap_action:
      action: navigate
      navigation_path: /lovelace/power
center:
  type: bars
  content:
    - preset: ratio
      name: ratio
    - preset: custom
      entity: sensor.ss_battery_soc
      name: SOC
animation: slide
```

:::
