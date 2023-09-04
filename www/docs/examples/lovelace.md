# Lovelace examples

Thsis page contains a coupe of frontend examples to represent the power flow of your system. While the Home Assistant Energy dashboard give you a good indication of your energy usage, the power flow show you what is happening at the current moment.

## Sunsynk Power Flow Card

The Sunsynk Power Flow card can be installed by adding a custom Lovelace repository to HACS: <https://github.com/slipx06/sunsynk-power-flow-card> or clicking this button:

[![Open your Home Assistant instance and open slipx's repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=sunsynk-power-flow-card&category=plugin&owner=slipx06)

![Power Flow Card](../images/power-flow.webp =500x600)

```yaml
SENSORS:
  - power_flow_card
```

::: details Lovelace yaml

```yaml
type: custom:sunsynk-power-flow-card
cardstyle: full
show_solar: true
large_font: true
battery:
  energy: 11000
  shutdown_soc: 20
  invert_power: false
  colour: var(--energy-battery-in-color)
  show_daily: false
solar:
  colour: var(--energy-solar-color)
  show_daily: false
  mppts: 1
entities:
  use_timer_248: switch.ss_use_timer
  priority_load_243: switch.ss_priority_load
  inverter_voltage_154: sensor.ss_grid_voltage
  inverter_load_freq_192: sensor.ss_grid_frequency
  inverter_current_164: sensor.ss_inverter_current
  inverter_power_175: sensor.ss_inverter_power
  grid_connected_status_194: binary_sensor.ss_grid_connected
  inverter_status_59: sensor.ss_overall_state
  batchargeday_70: sensor.ss_day_battery_charge
  batdischargeday_71: sensor.ss_day_battery_discharge
  battery_voltage_183: sensor.ss_battery_voltage
  battery_soc_184: sensor.ss_battery_soc
  battery_power_190: sensor.ss_battery_power
  battery_current_191: sensor.ss_battery_current
  grid_power_169: sensor.ss_grid_power
  grid_buy_day_76: sensor.ss_day_grid_import
  grid_sell_day_77: sensor.ss_day_grid_export
  grid_ct_power_172: sensor.ss_grid_ct_power
  loadday_84: sensor.ss_day_load_energy
  load_frequency_192: sensor.ss_load_frequency
  essential_power: sensor.ss_essential_power
  nonessential_power: sensor.ss_non_essential_power
  aux_power_166: sensor.ss_aux_power
  solarday_108: sensor.ss_day_pv_energy
  pv1_power_186: sensor.ss_pv1_power
  pv1_v_109: sensor.ss_pv1_voltage
  pv1_i_110: sensor.ss_pv1_current
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
