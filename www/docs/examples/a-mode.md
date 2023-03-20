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
