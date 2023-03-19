# Templates

You can view sensor values under Home Assistant using the "Developer Tools" -> Templates tab.

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
