# ESP integration

The ESP integration uses a combination of mysensors + Frontend

Init your ESP sensor with the following **mysensors.py** entry

```python
try:
    from ha_addon_sunsynk_multi.esp import ESP
    ESP(
        api_key="xxxxxxxx-xxxxxxxx-xxxxxxxx-xxxxxxxx",
        area_id="jhbcitypower2-2-victorypark",
        ha_prefix="eskom_vp",
    )
except ImportError:
    pass
```

The following should be saved in you HA config folder `/config/custom_templates/loadshed.jinja`

```jinja
{% macro loadshed_md(espnext) %}

{%- set active = (as_timestamp(states(espnext))<=as_timestamp(now())) | bool %}
{%- set stage = state_attr(espnext, "note") %}
{%- set t0 = state_attr(espnext, "start") | as_timestamp | int %}
{%- set t1 = state_attr(espnext, "end") | as_timestamp | int %}
{%- set t0_min = (t0|int - as_timestamp(now()))|int // 60 %}
{%- set t1_min = (t1|int - as_timestamp(now()))|int // 60 %}

{%- if stage %}
{%- if not bool(active) %}
{%- set mins = t0_min % 60 %}
{%- set hrs = t0_min // 60 %}
{%- set alert = "Load Shedding starts in {h}:{m:02d} ({next})".format(m=mins, h=hrs, next=t0 |
timestamp_custom("%H:%M", True)) %}
{%- if hrs>12 %}
<ha-alert alert-type="success">{{ alert }}</ha-alert>
{%- elif hrs > 1 %}
<ha-alert alert-type="warning">{{ alert }}</ha-alert>
{%- else %}
<ha-alert alert-type="error">{{ alert }}</ha-alert>
{%- endif %}
{%- else %}
{%- set mins = t1_min % 60 %}
{%- set hrs = t1_min // 60 %}
{%- set alert = "Load Shedding ends in {h}:{m:02d} ({next})".format(m=mins, h=hrs, next=t1 |
timestamp_custom("%H:%M", True)) %}
<ha-alert alert-type="error">{{ alert }}</ha-alert>
{%- endif %}
{%- else %}
{%- set mins = t0_min % 60 %}
{%- set hrs = t0_min // 60 % 24 %}
{%- set days = t0_min // 1440 %}
{%- if (t0 == 0 or t1 == 0) %}
{%- set alert = "No Load Shedding" %}
{%- else %}
{%- set alert = "Stage {stage} starts in {d}d {h:02d}:{m:02d} ({next})".format(stage=stage, d=days, m=mins, h=hrs,
next=as_timestamp(start_time) | timestamp_custom("%H:%M", True)) %}
{%- endif %}
<ha-alert alert-type="success">{{ alert }}</ha-alert>
{%- endif %}

{% endmacro %}
```

You can now add this card to your frontend to create a status of loadshedding

```yaml
  - type: markdown
    content: '{% from "loadshed.jinja" import loadshed_md %} {{ loadshed_md("sensor.eskom_vp_next") }}'
```
