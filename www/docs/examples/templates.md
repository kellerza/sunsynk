# Templates

You can view sensor values under Home Assistant using the "Developer Tools" -> Templates tab.

::: details Template details
```yaml
Essentials:     {{ states("sensor.ss_essential_power") }} W
Non-Essentials: {{ states("sensor.ss_non_essential_power") }} W
Grid CT:        {{ states("sensor.ss_grid_ct_power") }} W

Battery:
  {{ states("sensor.ss_battery_power") }} W
  {{ states("sensor.ss_battery_voltage") }} V
  {{ states("sensor.ss_battery_current") }} Amps
  {{ states("sensor.ss_battery_temperature") }} °C

Grid Power:
  {{ states("sensor.ss_grid_power") }} W
  {{ states("sensor.ss_grid_frequency") }} Hz
  {{ states("sensor.ss_grid_voltage") }} V
  {{ states("sensor.ss_grid_current") }} Amp
  CT {{ states("sensor.ss_grid_ct_power") }} W

Inverter
  {{ states("sensor.ss_inverter_power") }} W
  {{ states("sensor.ss_inverter_frequency") }} Hz

Load
  {{ states("sensor.ss_essential_power") }} W
  {{ states("sensor.ss_grid_frequency") }} Hz
  {{ states("sensor.ss_grid_voltage") }} V
  {{ states("sensor.ss_grid_current") }} Amp

PV1
  {{ states("sensor.ss_pv1_power") }} W
  {{ states("sensor.ss_pv1_voltage") }} V
  {{ states("sensor.ss_pv1_current") }} A
```
:::

## ESP API integration

ESP (EskomSePush) allows you to fetch the loadshedding schedules in South Africa through an API.

Get your API token and area [here](https://eskomsepush.gumroad.com/l/api) and add your api token & area to your secrets `/config/secrets.yaml`:
```yaml
esp_key: 069FXXXX-1A7FXXXX-AF06XXXX-6C2EXXXX
esp_area: jhbcitypower2-2-xxxxxx
```

The configuration can easily be added using HASS configuraition modules


::: details esp.yaml config module
Add the following to `/config/modules/esp.yaml`

```yaml
rest:
  - resource: "https://developer.sepush.co.za/business/2.0/area"
    scan_interval: '01:00:00' # RATE LIMIT!
    headers:
      Token: !secret esp_key
    params:
      id: !secret esp_area
    sensor:
      - name: EskomSePush
        force_update: true
        value_template: "OK"
        json_attributes:
          - events
          - info
          - schedule

sensor:
  #EskomSePush sensor
  - platform: rest
    name: EskomSePushAllowance
    resource: "https://developer.sepush.co.za/business/2.0/api_allowance"
    headers:
      Token: !secret esp_key
    json_attributes_path: "$.allowance"
    json_attributes:
      - count
      - limit
      - type
    value_template: "OK"
    scan_interval: 3600

  # template sensors based on ESP above
  - platform: template
    sensors:
      next_loadshedding_time:
        friendly_name: Next loadshedding time
        device_class: timestamp
        unique_id: Next_Loadshedding_Time
        value_template: "{{ state_attr('sensor.eskomsepush','events')[0].start }}"
      next_loadshedding_event:
        friendly_name: Next loadshedding event
        unique_id: Next_Loadshedding_Event
        value_template: "{{ state_attr('sensor.eskomsepush','events')[0].note }}"
      next_loadshedding_time_end:
        friendly_name: Next loadshedding end time
        unique_id: Next_Loadshedding_End_Time
        device_class: timestamp
        value_template: "{{ state_attr('sensor.eskomsepush','events')[0].end }}"
      next_loadshedding_duration:
        friendly_name: Next loadshedding duration
        unique_id: Next_Loadshedding_Duration
        unit_of_measurement: mins
        value_template: '{{ [( as_timestamp(states.sensor.next_loadshedding_time_end.state) | int - as_timestamp(states.sensor.next_loadshedding_time.state) | int ) / 60,-1] | max | round(0) }}'
      time_till_loadshedding:
        friendly_name: Time until next loadshedding
        unique_id: Time_Until_Next_Loadshedding
        unit_of_measurement: mins
        value_template: '{{ [( as_timestamp(states.sensor.next_loadshedding_time.state) | int - as_timestamp(now()) | int ) / 60,-1] | max | round(0) }}'
      time_till_loadshedding_ends:
        friendly_name: Time until next loadshedding ends
        unique_id: Time_Until_Next_Loadshedding_ends
        unit_of_measurement: mins
        value_template: '{{ [( as_timestamp(states.sensor.next_loadshedding_time_end.state) | int - as_timestamp(now()) | int ) / 60,-1] | max | round(0) }}'

      eskomsepush_calls_remaining:
        friendly_name: EskomSePush API Calls remaining
        unique_id: EskomSePush_calls_remaining
        value_template: '{{ int(state_attr("sensor.eskomsepushallowance","limit")) - int(state_attr("sensor.eskomsepushallowance","count")) }}'

      loadshedding_slot_forecast:
        friendly_name: Loadshedding slot forecast
        unique_id: loadshedding_slot_forecast
        value_template: >
          {%- for event in states['sensor.eskomsepush'].attributes.events -%} {{
          as_timestamp(event['start']) | timestamp_custom('%a %d %b:') }} {{ event['note'] }} {{
          as_timestamp(event['start']) | timestamp_custom('from %H:%M') }} to {{
          as_timestamp(event['end']) | timestamp_custom('%H:%M') }}
          {{- '\n' -}} {%- endfor -%}

binary_sensor:
  - platform: template
    sensors:
      loadshedding_active:
        friendly_name: "Loadshedding active"
        device_class: problem
        value_template: >
            {% if (int(states('sensor.time_till_loadshedding')) <= 0 ) %}
             True
            {% else %}
             False
            {% endif %}
```
:::

::: details Lovelace config

Add a custom card to Lovelace and use the following yaml
```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-chips-card
    chips:
      - type: entity
        entity: binary_sensor.load_shedding
        icon: ''
      - type: entity
        entity: sensor.next_loadshedding_event
        icon: ''
      - type: template
        content: '{{state_attr(entity, "count")}}/{{state_attr(entity, "limit")}}'
        entity: sensor.eskomsepushallowance
        icon: mdi:api
        tap_action:
          action: more-info
    alignment: center
  - type: markdown
    content: |2-
            {%- set active = is_state("binary_sensor.loadshedding_active", "on") %}
            {%- set stage = states("sensor.next_loadshedding_event") %}
            {%- set start_time = states("sensor.next_loadshedding_time") | as_timestamp | int %}
            {%- set end_time = states("sensor.next_loadshedding_time_end") | as_timestamp | int %}
            {%- set starts_min = ( start_time | int - as_timestamp(now()) | int ) // 60 %}
            {%- set ends_min = ( end_time | int - as_timestamp(now())) | int // 60 %}
            {%- if stage %}
              {%- if not bool(active) %}
                {%- set mins = starts_min % 60 %}
                {%- set hrs = starts_min // 60 %}
                {%- set alert = "Load Shedding starts in {h}h {m}m ({next})".format(m=mins, h=hrs, next=start_time | timestamp_custom("%H:%M", True)) %}
                {%- if hrs>12 %}
                  <ha-alert alert-type="success">{{ alert }}</ha-alert>
                {%- elif hrs > 1 %}
                  <ha-alert alert-type="warning">{{ alert }}</ha-alert>
                {%- else %}
                  <ha-alert alert-type="error">{{ alert }}</ha-alert>
                {%- endif %}
              {%- else %}
                  {%- set mins = ends_min % 60 %}
                  {%- set hrs = ends_min // 60 %}
                  {%- set alert = "Load Shedding ends in {h}h {m}m ({next})".format(m=mins, h=hrs, next=end_time | timestamp_custom("%H:%M", True)) %}
                  <ha-alert alert-type="error">{{ alert }}</ha-alert>
              {%- endif %}
            {%- else %}
              {%- set mins = starts_min % 60 %}
              {%- set hrs = starts_min // 60 % 24 %}
              {%- set days = starts_min // 1440 %}
              {%- if (start_time == 0 or end_time == 0) %}
              {%- set alert = "No Load Shedding" %}
              {%- else %}
              {%- set alert = "Stage {stage} starts in {d}d {h}h {m}m ({next})".format(stage=stage, d=days, m=mins, h=hrs, next=as_timestamp(start_time) | timestamp_custom("%H:%M", True)) %}
              {%- endif %}
              <ha-alert alert-type="success">{{ alert }}</ha-alert>
            {%- endif %}
```
:::
