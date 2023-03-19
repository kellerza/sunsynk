# System settings card

Below is an example Lovelace card to show the System mode in the frontend

::: Details
```yaml
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: entity
        entity: select.ss_prog1_time
        name: '1'
      - type: entity
        entity: select.ss_prog1_charge
        name: ' '
        state_color: false
      - type: gauge
        entity: number.ss_prog1_capacity
        needle: false
        name: ' '
  - type: horizontal-stack
    cards:
      - type: entity
        entity: select.ss_prog2_time
        name: '2'
      - type: entity
        entity: select.ss_prog2_charge
        name: ' '
        state_color: false
      - type: gauge
        entity: number.ss_prog2_capacity
        needle: false
        name: ' '
  - type: horizontal-stack
    cards:
      - type: entity
        entity: select.ss_prog3_time
        name: '3'
      - type: entity
        entity: select.ss_prog3_charge
        name: ' '
        state_color: false
      - type: gauge
        entity: number.ss_prog3_capacity
        needle: false
        name: ' '
  - type: horizontal-stack
    cards:
      - type: entity
        entity: select.ss_prog4_time
        name: '4'
      - type: entity
        entity: select.ss_prog4_charge
        name: ' '
        state_color: false
      - type: gauge
        entity: number.ss_prog4_capacity
        needle: false
        name: ' '
  - type: horizontal-stack
    cards:
      - type: entity
        entity: select.ss_prog5_time
        name: '5'
      - type: entity
        entity: select.ss_prog5_charge
        name: ' '
        state_color: false
      - type: gauge
        entity: number.ss_prog5_capacity
        needle: false
        name: ' '
  - type: horizontal-stack
    cards:
      - type: entity
        entity: select.ss_prog6_time
        name: '6'
      - type: entity
        entity: select.ss_prog6_charge
        name: ' '
        state_color: false
      - type: gauge
        entity: number.ss_prog6_capacity
        needle: false
        name: ' '
```
:::