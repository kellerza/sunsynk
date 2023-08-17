# System settings card

Below you can find two examples Lovelace cards to show, and allow editing, of the System mode in the frontend

## Example #1

This card shows the system values and can be edited by clicking on individual settings. It uses the Mushroom cards, which can be installed with HACS.

You need the following sensor group.

```yaml
SENSORS:
  - settings
  - load_limit
```

![settings](../images/system_settings.webp)

::: details Lovelace yaml

```yaml
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: select.ss_prog1_time
        fill_container: true
        secondary_info: none
        primary_info: state
        icon: mdi:numeric-1
      - type: vertical-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: select.ss_prog1_charge
            name: ' '
            fill_container: false
            icon_type: none
          - type: custom:mushroom-entity-card
            entity: number.ss_prog1_power
            name: ' '
            icon_type: none
      - type: gauge
        entity: number.ss_prog1_capacity
        name: ' '
        needle: false
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: select.ss_prog2_time
        fill_container: true
        secondary_info: none
        primary_info: state
        icon: mdi:numeric-2
      - type: vertical-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: select.ss_prog2_charge
            name: ' '
            fill_container: false
            icon_type: none
          - type: custom:mushroom-entity-card
            entity: number.ss_prog2_power
            name: ' '
            icon_type: none
      - type: gauge
        entity: number.ss_prog2_capacity
        needle: false
        name: ' '
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: select.ss_prog3_time
        fill_container: true
        secondary_info: none
        primary_info: state
        icon: mdi:numeric-3
      - type: vertical-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: select.ss_prog3_charge
            name: ' '
            fill_container: false
            icon_type: none
          - type: custom:mushroom-entity-card
            entity: number.ss_prog3_power
            name: ' '
            icon_type: none
      - type: gauge
        entity: number.ss_prog3_capacity
        needle: false
        name: ' '
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: select.ss_prog4_time
        fill_container: true
        secondary_info: none
        primary_info: state
        icon: mdi:numeric-4
      - type: vertical-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: select.ss_prog4_charge
            name: ' '
            fill_container: false
            icon_type: none
          - type: custom:mushroom-entity-card
            entity: number.ss_prog4_power
            name: ' '
            icon_type: none
      - type: gauge
        entity: number.ss_prog4_capacity
        needle: false
        name: ' '
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: select.ss_prog5_time
        fill_container: true
        secondary_info: none
        primary_info: state
        icon: mdi:numeric-5
      - type: vertical-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: select.ss_prog5_charge
            name: ' '
            fill_container: false
            icon_type: none
          - type: custom:mushroom-entity-card
            entity: number.ss_prog5_power
            name: ' '
            icon_type: none
      - type: gauge
        entity: number.ss_prog5_capacity
        needle: false
        name: ' '
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: select.ss_prog6_time
        fill_container: true
        secondary_info: none
        primary_info: state
        icon: mdi:numeric-6
      - type: vertical-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: select.ss_prog6_charge
            name: ' '
            fill_container: false
            icon_type: none
          - type: custom:mushroom-entity-card
            entity: number.ss_prog6_power
            name: ' '
            icon_type: none
      - type: gauge
        entity: number.ss_prog6_capacity
        needle: false
        name: ' '
  - type: entity
    entity: select.ss_load_limit
```

:::

## Example #2

Another example of a panel to control the Turbo Energy inverter system work mode from Home Assistant

This panel is editable directly from the frontend and includes sensors `prog1_mode` to `prog6_mode`

::: details Lovelace yaml

```yaml
  - theme: Backend-selected
    title: Bateria
    path: bateria
    icon: mdi:battery
    badges: []
    cards:
      - type: entities
        entities:
          - entity: select.prog1_time
            name: Hora
          - entity: number.prog1_power
            name: Potencia maxima
          - entity: select.prog1_mode
            name: Modo
          - entity: number.prog1_capacity
            name: Minimo Bateria
        title: Horario 1
      - type: entities
        entities:
          - entity: select.prog2_time
            name: Hora
          - entity: number.prog2_power
            name: Potencia maxima
          - entity: select.prog2_mode
            name: Modo
          - entity: number.prog2_capacity
            name: Minimo Bateria
        title: Horario 2
      - type: entities
        entities:
          - entity: select.prog3_time
            name: Hora
          - entity: number.prog3_power
            name: Potencia maxima
          - entity: select.prog3_mode
            name: Modo
          - entity: number.prog3_capacity
            name: Minimo Bateria
        title: Horario 3
      - type: entities
        entities:
          - entity: select.prog4_time
            name: Hora
          - entity: number.prog4_power
            name: Potencia maxima
          - entity: select.prog4_mode
            name: Modo
          - entity: number.prog4_capacity
            name: Minimo Bateria
        title: Horario 4
      - type: entities
        entities:
          - entity: select.prog5_time
            name: Hora
          - entity: number.prog5_power
            name: Potencia maxima
          - entity: select.prog5_mode
            name: Modo
          - entity: number.prog5_capacity
            name: Minimo Bateria
        title: Horario 5
      - type: entities
        entities:
          - entity: select.prog6_time
            name: Hora
          - entity: number.prog6_power
            name: Potencia maxima
          - entity: select.prog6_mode
            name: Modo
          - entity: number.prog6_capacity
            name: Minimo Bateria
        title: Horario 6
```

:::
