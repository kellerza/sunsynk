# ESP add-on

::: info

Install from the <https://github.com/kellerza/hass-addons> repository.

[![Open your Home Assistant instance and add the kellerza/hass-addons URL](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fkellerza%2Fhass-addons)

:::

ESP (EskomSePush) allows you to fetch the loadshedding schedules in South Africa through an API.

You need your own API key, get it here: <https://eskomsepush.gumroad.com/l/api>

::: tip

The EskomSePush API is limited to 50 requests per day. Request results are cached to reduce calls to the API.

:::

For each AREA, you need the following:

- `API_KEY`
- `HA_PREFIX`
- `AREA_ID` *

You can search for the AREA_ID using the `SEARCH_AREA` configuration option. The search result will be printed in the addon log

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
