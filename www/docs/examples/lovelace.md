# Power Distribution card

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