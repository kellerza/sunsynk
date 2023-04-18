# System Mode Automation

## Battery charging to optimise Time-of-Use tariffs

Example of automation to economically optimize the battery: In Spain, electrical surpluses are better paid early in the day, the inverter usually charges the battery at that time so there are no surpluses.  Later, when they are already charged, the purchase price of surpluses is usually much lower, which is why it occurred to us in the ["Posesos del Turbo..."](https://t.me/pos_turbo_energy) Telegram group in Spain to make an automation by lowering the maximum charging power of the battery to 1A during the first hours of the day to force the sale of surpluses at those hours, and then, for example from 12 or 1 pm, when the sale price drops, raise the charging power to its normal level to charge it before sunset.  This will depend a lot on the number of plates, batteries and hours of light that each one has naturally.

::: details Automation details
```yaml
alias: Bajar potencia de carga
description: Inject surpluses
trigger:
  - platform: time
    at: "09:00:00"
condition: []
action:
  - device_id: #####################
    domain: number
    entity_id: number.battery_max_charge_current
    type: set_value
    value: 1
mode: single
```

and
```yaml
alias: Subir potencia de carga
description: Cargar bateria
trigger:
  - platform: time
    at: "13:00:00"
condition: []
action:
  - device_id: ######################
    domain: number
    entity_id: number.battery_max_charge_current
    type: set_value
    value: 75
mode: single
```
:::

## Charge the battery in case of low forecast

Example of automation to Charge the battery in the program 1 time in the months of March and September if the expected production of the following day is going to be less than 10kwh as long as the price in that hourly period is less than 0.05cts. Using the Forecast.Solar integration.

::: details Automation details
```yaml
alias: Cargar bateria noche
description: ""
trigger:
  - platform: time
    at: "23:55:00"
condition:
  - condition: template
    value_template: "{{ now().month in [3, 9] }} "
    alias: "Marzo y Septiembre "
  - condition: numeric_state
    entity_id: sensor.energy_production_tomorrow
    below: 15
  - condition: numeric_state
    entity_id: sensor.esios_pvpc
    attribute: price_next_day_00h
    below: 0.05
action:
  - device_id: 1d0794ae215d5051bf06926b63209edf
    domain: select
    entity_id: select.prog1_mode
    type: select_option
    option: Charge
mode: single
```
:::

## Load Limit

Ideally you do not want to discharge your batteries into non-essential loads like the geyser or heat pumps.

With **Load Limit** you can change the power export behavior from your inverter. The power from your inverter is a combination of PV and battery.

The options are:
- **Essentials** - only supply power to the essentials (after the inverter)
- **Allow Export** - allow export to the grid. This can feed power to the non-essential loads and places no limit to feeding back into the grid.
- **Zero Export** - allow feed back to the grid side, or non-essentials. In addition it uses the Inverter's CT to limit power fed back toward the utility grid.

This automation sets `load_limit` for daytime & night-time behavior:
- During the day, the inverter (PV & battery) can supply excess power to the non-essentials. No/zero export is allowed, since we cannot sell power to the grid.
- During the evening, the inverter (PV & battery) should only supply power to the Essentials. All non-essentials can use the utility grid if available.

```yaml
SENSORS:
  - load_limit
```

::: details Automations
Automation 1
```yaml
alias: SS Load Limit Essentials
trigger:
  - platform: time
    at: "18:30:00"
condition: []
action:
  - service: select.select_option
    data:
      option: Essentials
    target:
      entity_id: select.ss_load_limit
mode: single
```

Automation 2
```yaml
alias: SS Load Limit Zero Export
trigger:
  - platform: time
    at: "07:00:00"
condition: []
action:
  - service: select.select_option
    data:
      option: Zero Export
    target:
      entity_id: select.ss_load_limit
mode: single
```
:::


## Detecting power failures / Load shedding

This can be achieved with any of the following sensors

- `Grid connected status`
- `Grid frequency` drops below a certain value
- `Grid voltage` drops below a certain value

The example automation below creates a binary_sensor from the grid frequency and sends out notification on power failure and the duration of the failure (with some sane back-offs). It serves as a reminder that load shadding is a reality.

:: details Configuration package (yaml)
Place this file in `/config/packages/alert.yaml` and enable configuration for the `packages` folder (refer to the HA docs [here](https://www.home-assistant.io/docs/configuration/packages/#create-a-packages-folder))

```yaml
template:
  binary_sensor:
    - name: Load shedding
      state: "{{ states('sensor.ss_grid_frequency') | default (50) | int(0) < 40  }}"

alert:
  load_shed:
    name: "Load shedding"
    message: "The power is off for - {{ relative_time(states.binary_sensor.load_shedding.last_changed) }}"
    done_message: "The power is back on"
    entity_id: binary_sensor.load_shedding
    repeat:
      - 2
      - 30
      - 60
      - 120
    can_acknowledge: true  # Optional, default is true
    skip_first: true  # Optional, false is the default
    notifiers:
      - mobile_app_johann_iphone
```
:::
